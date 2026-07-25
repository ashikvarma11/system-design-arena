from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.persistence.db import SessionLocal
from app.services import debate_service, session_service

router = APIRouter(prefix="/api/v1/sessions", tags=["debate"])

_STREAMABLE_STATUSES = ("brief_created", "failed")


@router.get("/{session_id}/stream")
def stream_debate(session_id: str):
    db = SessionLocal()
    session = session_service.get_session(db, session_id)
    if session is None:
        db.close()
        raise HTTPException(status_code=404, detail="session not found")
    if session.status not in _STREAMABLE_STATUSES:
        current_status = session.status
        db.close()
        raise HTTPException(
            status_code=409,
            detail=f"session is not in a streamable state (status={current_status})",
        )

    if session.status == "failed":
        session_service.reset_session_for_retry(db, session)

    def event_source():
        try:
            yield from debate_service.stream_debate(db, session)
        finally:
            db.close()

    return StreamingResponse(event_source(), media_type="text/event-stream")
