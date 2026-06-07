"""Shared helpers for fal.ai queue API scripts."""

from __future__ import annotations

import sys
from typing import Any

import fal_client
from fal_client import FalClientHTTPError

from api_errors import exit_on_api_error
from env_utils import load_env_file, require_env


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
    load_env_file()
    require_env("FAL_KEY")
    try:
        return fal_client.subscribe(
            model_id,
            arguments=arguments,
            with_logs=True,
            on_queue_update=on_queue_update,
        )
    except FalClientHTTPError as exc:
        exit_on_api_error(exc)
