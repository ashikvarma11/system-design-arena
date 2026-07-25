from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProblemBrief(BaseModel):
    goals: list[str]
    constraints: list[str]
    non_goals: list[str]


class SessionCreateRequest(BaseModel):
    text: str


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
