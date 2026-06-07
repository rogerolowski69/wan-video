"""Load `.env` and validate required environment variables."""

from __future__ import annotations

import os
from pathlib import Path

from paths import ENV_FILE


def load_env_file(env_path: Path | None = None) -> None:
    """Populate os.environ from a `.env` file (does not override existing vars)."""
    path = env_path or ENV_FILE
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def require_env(name: str) -> str:
    """Return an environment variable or exit with a clear message."""
    load_env_file()
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"{name} is not set. Add it to .env or your environment.")
    return value
