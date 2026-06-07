"""JWT issue and verification for authenticated sessions."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt

ALGORITHM = "HS256"
DEFAULT_EXPIRY_DAYS = 7


def jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET", "")
    if not secret:
        secret = "dev-insecure-change-me"
    return secret


def create_access_token(user_id: int, *, expires_days: int = DEFAULT_EXPIRY_DAYS) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=expires_days),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, jwt_secret(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    payload = jwt.decode(token, jwt_secret(), algorithms=[ALGORITHM])
    return int(payload["sub"])
