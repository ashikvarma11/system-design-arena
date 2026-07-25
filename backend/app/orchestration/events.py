from dataclasses import dataclass, field
from typing import Any


@dataclass
class DebateEvent:
    """One SSE event. `type` is one of: turn_start, turn_end, plan, done, error."""

    type: str
    data: dict[str, Any] = field(default_factory=dict)
