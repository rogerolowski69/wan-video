"""Project paths — single source of truth anchored at the repo root."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "output"
DATA_DIR = PROJECT_ROOT / "data"
ENV_FILE = PROJECT_ROOT / ".env"
DB_FILE = DATA_DIR / "wan_video.db"


def project_relative(path: Path | str) -> Path:
    """Resolve a relative path against PROJECT_ROOT; leave absolute paths unchanged."""
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def default_database_url() -> str:
    """SQLite URL with forward slashes (safe on Windows)."""
    return f"sqlite:///{DB_FILE.as_posix()}"
