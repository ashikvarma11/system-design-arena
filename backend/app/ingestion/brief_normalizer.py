import json

from app.core.llm_client import get_llm_client
from app.persistence.schemas import ProblemBrief

_SYSTEM_PROMPT = """You are a system design intake assistant. Given a raw problem \
description (which may be informal, a chat message, or an architecture-decision \
document), extract a structured problem brief.

Respond with ONLY a JSON object of this exact shape:
{"goals": ["..."], "constraints": ["..."], "non_goals": ["..."]}

- goals: what the system must achieve, as short imperative statements.
- constraints: hard limits mentioned or clearly implied (scale, latency, budget, \
compliance, team size, tech stack, etc).
- non_goals: things explicitly or implicitly out of scope.

If a category has no clear items, return an empty list for it. Do not invent \
requirements that aren't supported by the input."""


def normalize_brief(raw_text: str) -> ProblemBrief:
    client = get_llm_client()
    raw_response = client.complete(_SYSTEM_PROMPT, raw_text, json_mode=True)
    data = json.loads(raw_response)
    return ProblemBrief(
        goals=data.get("goals", []),
        constraints=data.get("constraints", []),
        non_goals=data.get("non_goals", []),
    )
