"""ORM models for tracking API generation runs and saved artifacts."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class GenerationRun(Base):
    __tablename__ = "generation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    script_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    model_id: Mapped[str] = mapped_column(String(256), nullable=False)
    backend: Mapped[str] = mapped_column(String(32), nullable=False)  # fal_direct | hf_inference
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    artifacts: Mapped[list[OutputArtifact]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
    )


class OutputArtifact(Base):
    __tablename__ = "output_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("generation_runs.id", ondelete="CASCADE"), index=True)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_kind: Mapped[str] = mapped_column(String(32), nullable=False)  # image | video | model_3d | json | other
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    run: Mapped[GenerationRun] = relationship(back_populates="artifacts")
