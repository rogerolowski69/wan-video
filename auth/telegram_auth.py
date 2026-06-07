"""Validate Telegram Mini App initData per official WebApp HMAC rules."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any
from urllib.parse import parse_qsl


class TelegramAuthError(ValueError):
    pass


def bot_token() -> str | None:
    return os.environ.get("TELEGRAM_BOT_TOKEN") or None


def validate_init_data(init_data: str, *, max_age_seconds: int = 86_400) -> dict[str, Any]:
    token = bot_token()
    if not token:
        raise TelegramAuthError("TELEGRAM_BOT_TOKEN is not configured")

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise TelegramAuthError("Missing hash in initData")

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calculated_hash, received_hash):
        raise TelegramAuthError("Invalid initData signature")

    auth_date = int(parsed.get("auth_date", "0"))
    if auth_date <= 0:
        raise TelegramAuthError("Missing auth_date")
    if time.time() - auth_date > max_age_seconds:
        raise TelegramAuthError("initData expired")

    user_raw = parsed.get("user")
    if not user_raw:
        raise TelegramAuthError("Missing user in initData")

    user = json.loads(user_raw)
    if "id" not in user:
        raise TelegramAuthError("Invalid user payload")

    return user
