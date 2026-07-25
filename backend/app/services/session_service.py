from sqlalchemy.orm import Session

from app.ingestion.brief_normalizer import normalize_brief
from app.ingestion.file_extractors import extract_text
from app.persistence.models import SessionRecord


def create_session_from_text(db: Session, text: str) -> SessionRecord:
    return _create_session(db, text=text, input_type="text", filename=None)


def create_session_from_file(db: Session, filename: str, content: bytes) -> SessionRecord:
    text = extract_text(filename, content)
    return _create_session(db, text=text, input_type="file", filename=filename)


def _create_session(db: Session, *, text: str, input_type: str, filename: str | None) -> SessionRecord:
    brief = normalize_brief(text)

    record = SessionRecord(
        input_type=input_type,
        raw_input_text=text,
        raw_input_filename=filename,
        problem_brief_json=brief.model_dump(),
        status="brief_created",
        title=_derive_title(brief, text),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _derive_title(brief, text: str) -> str:
    if brief.goals:
        return brief.goals[0][:120]
    return text.strip().splitlines()[0][:120] if text.strip() else "Untitled session"


def get_session(db: Session, session_id: str) -> SessionRecord | None:
    return db.get(SessionRecord, session_id)


def list_sessions(db: Session) -> list[SessionRecord]:
    return db.query(SessionRecord).order_by(SessionRecord.created_at.desc()).all()
