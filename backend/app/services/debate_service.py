import json
from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.orchestration.events import DebateEvent
from app.orchestration.orchestrator import run_debate
from app.persistence.models import SessionRecord


def stream_debate(db: Session, session: SessionRecord) -> Iterator[str]:
    """Runs the debate and formats each DebateEvent as an SSE `data:` line."""
    for event in run_debate(db, session):
        yield _format_sse(event)


def _format_sse(event: DebateEvent) -> str:
    payload = json.dumps(event.data)
    return f"event: {event.type}\ndata: {payload}\n\n"
