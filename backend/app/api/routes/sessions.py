from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.persistence.db import get_db
from app.persistence.schemas import (
    RelatedSession,
    SessionCreateRequest,
    SessionDetailResponse,
    SessionListItem,
    SessionResponse,
)
from app.services import session_service

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])

_ALLOWED_EXTENSIONS = (".txt", ".md", ".pdf")


@router.post("", response_model=SessionResponse)
def create_session(payload: SessionCreateRequest, db: Session = Depends(get_db)):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="text must not be empty")
    record = session_service.create_session_from_text(db, payload.text, payload.rounds_planned)
    return record


@router.post("/upload", response_model=SessionResponse)
async def upload_session(
    file: UploadFile = File(...),
    rounds_planned: int = Form(default=3, ge=2, le=5),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(_ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail=f"unsupported file type, allowed: {_ALLOWED_EXTENSIONS}")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="uploaded file is empty")
    record = session_service.create_session_from_file(db, file.filename, content, rounds_planned)
    return record


@router.get("", response_model=list[SessionListItem])
def list_sessions(db: Session = Depends(get_db)):
    return session_service.list_sessions(db)


@router.get("/{session_id}", response_model=SessionDetailResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    record = session_service.get_session(db, session_id)
    if record is None:
        raise HTTPException(status_code=404, detail="session not found")
    return record


@router.get("/{session_id}/related", response_model=list[RelatedSession])
def get_related_sessions(session_id: str, db: Session = Depends(get_db)):
    record = session_service.get_session(db, session_id)
    if record is None:
        raise HTTPException(status_code=404, detail="session not found")
    return session_service.get_related_sessions(db, session_id)
