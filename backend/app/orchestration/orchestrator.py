import json
import re
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import Session

from app.core.llm_client import get_llm_client
from app.orchestration.events import DebateEvent
from app.orchestration.personas import CRITIC, DIMENSION_AGENTS, MODERATOR, PROPOSER, Persona
from app.persistence.db import SessionLocal
from app.persistence.models import AgreedPlanRecord, SessionRecord, TurnRecord
from app.persistence.schemas import ProblemBrief
from app.retrieval.vector_store import new_point_id, search_concepts, upsert_debate_turn

_RETRIEVAL_LIMIT = 3

_REBUTTING_RE = re.compile(r'REBUTTING:\s*"([^"]+)"', re.IGNORECASE)
_STATUS_RE = re.compile(r"STATUS:\s*(AGREE|DISAGREE)", re.IGNORECASE)


def run_debate(db: Session, session: SessionRecord) -> Iterator[DebateEvent]:
    """Bounded debate loop. Yields DebateEvents as it goes; persists every turn
    and the final AgreedPlanRecord. Never loops unboundedly: rounds_planned
    fixes the maximum number of iterations, though the loop can stop earlier
    if the team converges (every persona signals STATUS: AGREE in the same
    round)."""

    brief = ProblemBrief.model_validate(session.problem_brief_json)
    rounds_planned = session.rounds_planned

    try:
        session.status = "debating"
        db.commit()

        transcript: list[TurnRecord] = []
        converged = False

        proposal_turn = _run_turn(
            db, session, persona=PROPOSER, round_number=0,
            user_prompt=_kickoff_prompt(brief),
        )
        transcript.append(proposal_turn)
        yield DebateEvent("turn_end", _turn_payload(proposal_turn))

        for round_number in range(1, rounds_planned + 1):
            for persona in DIMENSION_AGENTS:
                yield DebateEvent("turn_start", {"persona": persona.name, "round_number": round_number})

            round_turns = _run_dimension_agents_concurrently(
                session.id, round_number, _group_discussion_prompt(brief, transcript),
            )
            for turn in round_turns:
                transcript.append(turn)
                yield DebateEvent("turn_end", _turn_payload(turn))

            yield DebateEvent("turn_start", {"persona": CRITIC.name, "round_number": round_number})
            critic_turn = _run_critic_turn(db, session, round_number, transcript)
            transcript.append(critic_turn)
            yield DebateEvent("turn_end", _turn_payload(critic_turn))

            if round_number >= 2 and _check_convergence(round_turns, critic_turn):
                converged = True
                break

            if round_number < rounds_planned:
                yield DebateEvent("turn_start", {"persona": PROPOSER.name, "round_number": round_number})
                proposal_turn = _run_turn(
                    db, session, persona=PROPOSER, round_number=round_number,
                    user_prompt=_revision_prompt(brief, transcript),
                )
                transcript.append(proposal_turn)
                yield DebateEvent("turn_end", _turn_payload(proposal_turn))

        plan_record = _run_moderator(db, session, transcript, converged)
        yield DebateEvent("plan", _plan_payload(plan_record))

        session.status = "completed"
        db.commit()
        yield DebateEvent("done", {"session_id": session.id})

    except Exception as exc:  # noqa: BLE001 - surface any failure as an SSE error event
        session.status = "failed"
        db.commit()
        yield DebateEvent("error", {"message": str(exc)})


def _run_turn(
    db: Session, session: SessionRecord, *, persona: Persona, round_number: int, user_prompt: str,
    critique_candidates: list[TurnRecord] | None = None, parse_status: bool = False,
) -> TurnRecord:
    concepts = _retrieve(persona, user_prompt)
    full_prompt = _augment_with_concepts(user_prompt, concepts)

    client = get_llm_client()
    content = client.complete(persona.system_prompt, full_prompt)

    target = _infer_critiqued_turn(content, critique_candidates) if critique_candidates else None
    status = _parse_agreement_status(content) if parse_status else None

    turn = TurnRecord(
        session_id=session.id,
        round_number=round_number,
        persona=persona.name,
        dimension=persona.dimension,
        content=content,
        critiques_turn_id=target.id if target else None,
        agreement_status=status,
        retrieved_concept_ids=[c["concept_id"] for c in concepts],
    )
    db.add(turn)
    db.commit()
    db.refresh(turn)

    upsert_debate_turn(
        new_point_id(),
        content,
        {
            "session_id": session.id,
            "turn_id": turn.id,
            "round_number": round_number,
            "persona": persona.name,
            "dimension": persona.dimension,
            "content_preview": content[:280],
            "problem_title": session.title,
            "created_at": turn.created_at.isoformat(),
        },
    )
    return turn


def _run_dimension_agents_concurrently(
    session_id: str, round_number: int, user_prompt: str,
) -> list[TurnRecord]:
    """Runs the three dimension agents (constraints/performance/security) in parallel
    threads -- they're independent reactions to the same discussion-so-far, so there's
    no reason to serialize LLM-bound I/O. Each thread opens its own DB session since
    SQLAlchemy Sessions aren't thread-safe; results are returned in DIMENSION_AGENTS
    order regardless of completion order, so downstream event ordering stays
    deterministic."""

    def _worker(persona: Persona) -> TurnRecord:
        thread_db = SessionLocal()
        try:
            thread_session = thread_db.get(SessionRecord, session_id)
            candidates = thread_db.query(TurnRecord).filter(
                TurnRecord.session_id == session_id
            ).all()
            turn = _run_turn(
                thread_db, thread_session, persona=persona, round_number=round_number,
                user_prompt=user_prompt, critique_candidates=candidates, parse_status=True,
            )
            thread_db.expunge(turn)
            return turn
        finally:
            thread_db.close()

    with ThreadPoolExecutor(max_workers=len(DIMENSION_AGENTS)) as pool:
        futures = [pool.submit(_worker, persona) for persona in DIMENSION_AGENTS]
        return [f.result() for f in futures]


def _run_critic_turn(
    db: Session, session: SessionRecord, round_number: int, transcript: list[TurnRecord],
) -> TurnRecord:
    prompt = _critic_prompt(transcript)
    return _run_turn(
        db, session, persona=CRITIC, round_number=round_number, user_prompt=prompt,
        critique_candidates=transcript, parse_status=True,
    )


def _run_moderator(
    db: Session, session: SessionRecord, transcript: list[TurnRecord], converged: bool,
) -> AgreedPlanRecord:
    prompt = _moderator_prompt(transcript, converged)
    client = get_llm_client()
    raw = client.complete(MODERATOR.system_prompt, prompt, json_mode=True)
    data = json.loads(raw)

    plan = AgreedPlanRecord(
        session_id=session.id,
        decision_summary=data.get("decision_summary", ""),
        constraints_addressed=data.get("constraints_addressed", []),
        performance_considerations=data.get("performance_considerations", []),
        security_considerations=data.get("security_considerations", []),
        open_risks=data.get("open_risks", []),
        converged=converged,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def _retrieve(persona: Persona, query: str) -> list[dict]:
    if persona.dimension is None:
        return []
    return search_concepts(query, limit=_RETRIEVAL_LIMIT, dimension_hint=persona.dimension)


def _augment_with_concepts(prompt: str, concepts: list[dict]) -> str:
    if not concepts:
        return prompt
    notes = "\n".join(f"- {c['title']}: {c['text']}" for c in concepts)
    return f"{prompt}\n\nReference concepts you may draw on:\n{notes}"


def _infer_critiqued_turn(content: str, candidates: list[TurnRecord]) -> TurnRecord | None:
    if not candidates:
        return None
    match = _REBUTTING_RE.search(content)
    if not match:
        return None
    quote = match.group(1).strip().lower()
    if not quote:
        return None
    for turn in candidates:
        if quote in turn.content.lower():
            return turn
    return None


def _parse_agreement_status(content: str) -> str | None:
    match = _STATUS_RE.search(content)
    if not match:
        return None
    return match.group(1).lower()


def _check_convergence(round_turns: list[TurnRecord], critic_turn: TurnRecord) -> bool:
    all_turns = [*round_turns, critic_turn]
    return all((t.agreement_status or "disagree") == "agree" for t in all_turns)


def _brief_text(brief: ProblemBrief) -> str:
    return (
        f"Goals: {'; '.join(brief.goals) or 'none stated'}\n"
        f"Constraints: {'; '.join(brief.constraints) or 'none stated'}\n"
        f"Non-goals: {'; '.join(brief.non_goals) or 'none stated'}"
    )


def _kickoff_prompt(brief: ProblemBrief) -> str:
    return f"Problem brief:\n{_brief_text(brief)}\n\nPropose an initial architecture."


def _transcript_text(transcript: list[TurnRecord]) -> str:
    return "\n\n".join(
        f"[turn_id={t.id}] Round {t.round_number} ({t.persona}): {t.content}" for t in transcript
    )


def _group_discussion_prompt(brief: ProblemBrief, transcript: list[TurnRecord]) -> str:
    return (
        f"Problem brief:\n{_brief_text(brief)}\n\n"
        f"Discussion so far:\n\n{_transcript_text(transcript)}\n\n"
        "Weigh in from your angle: react to the current proposal and to anything a teammate "
        "has said that touches your area."
    )


def _critic_prompt(transcript: list[TurnRecord]) -> str:
    return f"Discussion so far:\n\n{_transcript_text(transcript)}\n\nRebut the weakest point made."


def _revision_prompt(brief: ProblemBrief, transcript: list[TurnRecord]) -> str:
    return (
        f"Problem brief:\n{_brief_text(brief)}\n\n"
        f"Discussion so far:\n\n{_transcript_text(transcript)}\n\n"
        "Revise your proposal in response to what your teammates said, addressing them by name."
    )


def _moderator_prompt(transcript: list[TurnRecord], converged: bool) -> str:
    outcome = (
        "The team reached full agreement (everyone signaled STATUS: AGREE in the same round)."
        if converged
        else "The team did not fully agree; the discussion ended because it hit its round limit."
    )
    return (
        f"Full debate transcript:\n\n{_transcript_text(transcript)}\n\n"
        f"{outcome}\n\nSynthesize the final agreed plan."
    )


def _turn_payload(turn: TurnRecord) -> dict:
    return {
        "id": turn.id,
        "round_number": turn.round_number,
        "persona": turn.persona,
        "dimension": turn.dimension,
        "content": turn.content,
        "critiques_turn_id": turn.critiques_turn_id,
        "agreement_status": turn.agreement_status,
    }


def _plan_payload(plan: AgreedPlanRecord) -> dict:
    return {
        "id": plan.id,
        "decision_summary": plan.decision_summary,
        "constraints_addressed": plan.constraints_addressed,
        "performance_considerations": plan.performance_considerations,
        "security_considerations": plan.security_considerations,
        "open_risks": plan.open_risks,
        "converged": plan.converged,
    }
