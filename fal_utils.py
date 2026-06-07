"""Shared helpers for fal.ai queue API scripts."""

from __future__ import annotations

import sys
from typing import Any

import fal_client

from env_utils import require_env


def _safe_print(message: str) -> None:
    """Print fal queue logs without crashing on Windows cp1252 consoles."""
    encoding = sys.stdout.encoding or "utf-8"
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode(encoding, errors="replace").decode(encoding))


def on_queue_update(update: object) -> None:
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            _safe_print(log["message"])


def fal_subscribe(model_id: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Run a fal queue job with log streaming. Requires FAL_KEY."""
    require_env("FAL_KEY")
    return fal_client.subscribe(
        model_id,
        arguments=arguments,
        with_logs=True,
        on_queue_update=on_queue_update,
    )
