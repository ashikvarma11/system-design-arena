from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProblemBrief(BaseModel):
    goals: list[str]
    constraints: list[str]
    non_goals: list[str]


class SessionCreateRequest(BaseModel):
    text: str
    rounds_planned: int = Field(default=3, ge=2, le=5)


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    status: str
    input_type: str
    raw_input_filename: str | None
    problem_brief_json: ProblemBrief | None
    rounds_planned: int
    title: str | None


class SessionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    status: str
    title: str | None


class TurnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    round_number: int
    persona: str
    dimension: str | None
    content: str
    critiques_turn_id: str | None
    retrieved_concept_ids: list | None
    created_at: datetime


class AgreedPlan(BaseModel):
    decision_summary: str
    constraints_addressed: list[str]
    performance_considerations: list[str]
    security_considerations: list[str]
    open_risks: list[str]


class AgreedPlanResponse(AgreedPlan):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    created_at: datetime


class SessionDetailResponse(SessionResponse):
    turns: list[TurnResponse] = []
    agreed_plan: AgreedPlanResponse | None = None


class RelatedSession(BaseModel):
    session_id: str
    title: str | None
    status: str
    score: float
    matched_persona: str | None
    matched_snippet: str | None
