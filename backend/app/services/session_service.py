from sqlalchemy.orm import Session

from app.ingestion.brief_normalizer import normalize_brief
from app.ingestion.file_extractors import extract_text
from app.persistence.models import AgreedPlanRecord, SessionRecord, TurnRecord
from app.retrieval.vector_store import search_debate_turns


def create_session_from_text(db: Session, text: str, rounds_planned: int = 3) -> SessionRecord:
    return _create_session(db, text=text, input_type="text", filename=None, rounds_planned=rounds_planned)


def create_session_from_file(
    db: Session, filename: str, content: bytes, rounds_planned: int = 3
) -> SessionRecord:
    text = extract_text(filename, content)
    return _create_session(db, text=text, input_type="file", filename=filename, rounds_planned=rounds_planned)


def _create_session(
    db: Session, *, text: str, input_type: str, filename: str | None, rounds_planned: int = 3
) -> SessionRecord:
    brief = normalize_brief(text)

    record = SessionRecord(
        input_type=input_type,
        raw_input_text=text,
        raw_input_filename=filename,
        problem_brief_json=brief.model_dump(),
        status="brief_created",
        title=_derive_title(brief, text),
        rounds_planned=rounds_planned,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _derive_title(brief, text: str) -> str:
    if brief.goals:
        return brief.goals[0][:120]
    return text.strip().splitlines()[0][:120] if text.strip() else "Untitled session"


def reset_session_for_retry(db: Session, session: SessionRecord) -> None:
    """Clears turns and any partial plan from a failed session so a retry
    starts clean instead of duplicating rows alongside the failed attempt.
    Does not remove already-embedded turns from Qdrant's debate_turns
    collection -- harmless leftover data, not surfaced to users."""
    db.query(TurnRecord).filter(TurnRecord.session_id == session.id).delete()
    db.query(AgreedPlanRecord).filter(AgreedPlanRecord.session_id == session.id).delete()
    session.status = "brief_created"
    db.commit()


def get_session(db: Session, session_id: str) -> SessionRecord | None:
    return db.get(SessionRecord, session_id)


def list_sessions(db: Session) -> list[SessionRecord]:
    return db.query(SessionRecord).order_by(SessionRecord.created_at.desc()).all()


def get_related_sessions(db: Session, session_id: str, limit: int = 5) -> list[dict]:
    session = db.get(SessionRecord, session_id)
    if session is None:
        return []

    query_text = session.raw_input_text or session.title or ""
    if not query_text.strip():
        return []

    hits = search_debate_turns(query_text, limit=limit * 5, exclude_session_id=session_id)

    best_by_session: dict[str, dict] = {}
    for hit in hits:
        other_id = hit["session_id"]
        existing = best_by_session.get(other_id)
        if existing is None or hit["score"] > existing["score"]:
            best_by_session[other_id] = hit

    related = sorted(best_by_session.values(), key=lambda h: h["score"], reverse=True)[:limit]

    results = []
    for hit in related:
        other = db.get(SessionRecord, hit["session_id"])
        if other is None:
            continue
        results.append(
            {
                "session_id": other.id,
                "title": other.title,
                "status": other.status,
                "score": hit["score"],
                "matched_persona": hit.get("persona"),
                "matched_snippet": hit.get("content_preview"),
            }
        )
    return results
