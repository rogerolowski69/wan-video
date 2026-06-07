"""Database engine and session factory."""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from env_utils import load_env_file
from paths import DATA_DIR, default_database_url, project_relative

DEFAULT_DATABASE_URL = default_database_url()


def get_database_url() -> str:
    load_env_file()
    url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    # Railway/Heroku sometimes use postgres:// — SQLAlchemy expects postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def _sqlite_db_path(url: str) -> Path:
    raw = url.removeprefix("sqlite:///")
    path = Path(raw)
    if not path.is_absolute():
        path = project_relative(path)
    return path


def get_engine():
    url = get_database_url()
    if url.startswith("sqlite:///"):
        db_path = _sqlite_db_path(url)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, future=True, connect_args=connect_args)


SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)


def get_session() -> Session:
    return SessionLocal()
