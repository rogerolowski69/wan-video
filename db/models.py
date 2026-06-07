"""ORM models for tracking API generation runs and saved artifacts."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int | None] = mapped_column(Integer, nullable=True, unique=True, index=True)
    wallet_address: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    runs: Mapped[list[GenerationRun]] = relationship(back_populates="user")


class GenerationRun(Base):
    __tablename__ = "generation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
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
    user: Mapped[User | None] = relationship(back_populates="runs")


class OutputArtifact(Base):
    __tablename__ = "output_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("generation_runs.id", ondelete="CASCADE"), index=True)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_kind: Mapped[str] = mapped_column(String(32), nullable=False)  # image | video | model_3d | json | other
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    run: Mapped[GenerationRun] = relationship(back_populates="artifacts")
