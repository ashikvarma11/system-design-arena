import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SessionRecord(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    status: Mapped[str] = mapped_column(String(32), default="brief_created")
    input_type: Mapped[str] = mapped_column(String(16))  # "text" | "file"
    raw_input_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_input_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    problem_brief_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    rounds_planned: Mapped[int] = mapped_column(Integer, default=3)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    turns: Mapped[list["TurnRecord"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    agreed_plan: Mapped["AgreedPlanRecord | None"] = relationship(
        back_populates="session", cascade="all, delete-orphan", uselist=False
    )


class TurnRecord(Base):
    __tablename__ = "turns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"))
    round_number: Mapped[int] = mapped_column(Integer)
    persona: Mapped[str] = mapped_column(String(64))
    dimension: Mapped[str | None] = mapped_column(String(64), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    critiques_turn_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    retrieved_concept_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    token_usage_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    session: Mapped["SessionRecord"] = relationship(back_populates="turns")


class AgreedPlanRecord(Base):
    __tablename__ = "agreed_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"), unique=True)
    decision_summary: Mapped[str] = mapped_column(Text)
    constraints_addressed: Mapped[list | None] = mapped_column(JSON, nullable=True)
    performance_considerations: Mapped[list | None] = mapped_column(JSON, nullable=True)
    security_considerations: Mapped[list | None] = mapped_column(JSON, nullable=True)
    open_risks: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    session: Mapped["SessionRecord"] = relationship(back_populates="agreed_plan")
