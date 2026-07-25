import json
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
_RECENT_TURNS_FOR_CRITIC = 4


def run_debate(db: Session, session: SessionRecord) -> Iterator[DebateEvent]:
    """Bounded debate loop. Yields DebateEvents as it goes; persists every turn
    and the final AgreedPlanRecord. Never loops unboundedly: rounds_planned
    fixes the number of iterations."""

    brief = ProblemBrief.model_validate(session.problem_brief_json)
    rounds_planned = session.rounds_planned

    try:
        session.status = "debating"
        db.commit()

        transcript: list[TurnRecord] = []

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
                session.id, round_number, _dimension_prompt(brief, transcript, proposal_turn),
            )
            for turn in round_turns:
                transcript.append(turn)
                yield DebateEvent("turn_end", _turn_payload(turn))

            yield DebateEvent("turn_start", {"persona": CRITIC.name, "round_number": round_number})
            critic_turn = _run_critic_turn(db, session, round_number, transcript, round_turns)
            transcript.append(critic_turn)
            yield DebateEvent("turn_end", _turn_payload(critic_turn))

            if round_number < rounds_planned:
                yield DebateEvent("turn_start", {"persona": PROPOSER.name, "round_number": round_number})
                proposal_turn = _run_turn(
                    db, session, persona=PROPOSER, round_number=round_number,
                    user_prompt=_revision_prompt(brief, transcript, round_turns, critic_turn),
                )
                transcript.append(proposal_turn)
                yield DebateEvent("turn_end", _turn_payload(proposal_turn))

        plan_record = _run_moderator(db, session, transcript)
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
) -> TurnRecord:
    concepts = _retrieve(persona, user_prompt)
    full_prompt = _augment_with_concepts(user_prompt, concepts)

    client = get_llm_client()
    content = client.complete(persona.system_prompt, full_prompt)

    turn = TurnRecord(
        session_id=session.id,
        round_number=round_number,
        persona=persona.name,
        dimension=persona.dimension,
        content=content,
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
    threads -- they're independent reactions to the same proposal, so there's no reason
    to serialize LLM-bound I/O. Each thread opens its own DB session since SQLAlchemy
    Sessions aren't thread-safe; results are returned in DIMENSION_AGENTS order regardless
    of completion order, so downstream event ordering stays deterministic."""

    def _worker(persona: Persona) -> TurnRecord:
        thread_db = SessionLocal()
        try:
            thread_session = thread_db.get(SessionRecord, session_id)
            turn = _run_turn(
                thread_db, thread_session, persona=persona, round_number=round_number,
                user_prompt=user_prompt,
            )
            thread_db.expunge(turn)
            return turn
        finally:
            thread_db.close()

    with ThreadPoolExecutor(max_workers=len(DIMENSION_AGENTS)) as pool:
        futures = [pool.submit(_worker, persona) for persona in DIMENSION_AGENTS]
        return [f.result() for f in futures]


def _run_critic_turn(
    db: Session, session: SessionRecord, round_number: int,
    transcript: list[TurnRecord], round_turns: list[TurnRecord],
) -> TurnRecord:
    recent = round_turns if round_turns else transcript[-_RECENT_TURNS_FOR_CRITIC:]
    prompt = _critic_prompt(recent)
    concepts = _retrieve(CRITIC, prompt)
    full_prompt = _augment_with_concepts(prompt, concepts)

    client = get_llm_client()
    content = client.complete(CRITIC.system_prompt, full_prompt)

    target = _infer_critiqued_turn(content, recent)

    turn = TurnRecord(
        session_id=session.id,
        round_number=round_number,
        persona=CRITIC.name,
        dimension=CRITIC.dimension,
        content=content,
        critiques_turn_id=target.id if target else None,
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
            "persona": CRITIC.name,
            "dimension": CRITIC.dimension,
            "content_preview": content[:280],
            "problem_title": session.title,
            "created_at": turn.created_at.isoformat(),
        },
    )
    return turn


def _run_moderator(db: Session, session: SessionRecord, transcript: list[TurnRecord]) -> AgreedPlanRecord:
    prompt = _moderator_prompt(transcript)
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


def _infer_critiqued_turn(critic_content: str, candidates: list[TurnRecord]) -> TurnRecord | None:
    if not candidates:
        return None
    lowered = critic_content.lower()
    for turn in candidates:
        snippet = turn.content[:60].lower()
        if snippet and snippet[:20] in lowered:
            return turn
    return candidates[0]


def _brief_text(brief: ProblemBrief) -> str:
    return (
        f"Goals: {'; '.join(brief.goals) or 'none stated'}\n"
        f"Constraints: {'; '.join(brief.constraints) or 'none stated'}\n"
        f"Non-goals: {'; '.join(brief.non_goals) or 'none stated'}"
    )


def _kickoff_prompt(brief: ProblemBrief) -> str:
    return f"Problem brief:\n{_brief_text(brief)}\n\nPropose an initial architecture."


def _dimension_prompt(brief: ProblemBrief, transcript: list[TurnRecord], proposal_turn: TurnRecord) -> str:
    return (
        f"Problem brief:\n{_brief_text(brief)}\n\n"
        f"Current proposal (by Proposer):\n{proposal_turn.content}\n\n"
        "Evaluate this proposal from your assigned dimension."
    )


def _critic_prompt(recent: list[TurnRecord]) -> str:
    turns_text = "\n\n".join(f"[turn_id={t.id}] ({t.persona}): {t.content}" for t in recent)
    return f"Recent turns:\n\n{turns_text}\n\nRebut the weakest one."


def _revision_prompt(
    brief: ProblemBrief, transcript: list[TurnRecord], round_turns: list[TurnRecord], critic_turn: TurnRecord,
) -> str:
    feedback_text = "\n\n".join(f"({t.persona}): {t.content}" for t in round_turns)
    return (
        f"Problem brief:\n{_brief_text(brief)}\n\n"
        f"Feedback from this round:\n{feedback_text}\n\n"
        f"Critic's rebuttal:\n{critic_turn.content}\n\n"
        "Revise your proposal in response."
    )


def _moderator_prompt(transcript: list[TurnRecord]) -> str:
    turns_text = "\n\n".join(f"Round {t.round_number} ({t.persona}): {t.content}" for t in transcript)
    return f"Full debate transcript:\n\n{turns_text}\n\nSynthesize the final agreed plan."


def _turn_payload(turn: TurnRecord) -> dict:
    return {
        "id": turn.id,
        "round_number": turn.round_number,
        "persona": turn.persona,
        "dimension": turn.dimension,
        "content": turn.content,
        "critiques_turn_id": turn.critiques_turn_id,
    }


def _plan_payload(plan: AgreedPlanRecord) -> dict:
    return {
        "id": plan.id,
        "decision_summary": plan.decision_summary,
        "constraints_addressed": plan.constraints_addressed,
        "performance_considerations": plan.performance_considerations,
        "security_considerations": plan.security_considerations,
        "open_risks": plan.open_risks,
    }
