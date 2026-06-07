"""FastAPI dependencies for optional/required authentication."""

from __future__ import annotations

import os

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.jwt_utils import decode_access_token
from db.models import User
from db.session import get_session

_bearer = HTTPBearer(auto_error=False)


def auth_required() -> bool:
    return os.environ.get("AUTH_REQUIRED", "1").strip().lower() not in {"0", "false", "no"}


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> User | None:
    if credentials is None or credentials.scheme.lower() != "bearer":
        return None
    try:
        user_id = decode_access_token(credentials.credentials)
    except Exception:
        return None

    session = get_session()
    try:
        return session.get(User, user_id)
    finally:
        session.close()


def require_user(user: User | None = Depends(get_optional_user)) -> User:
    if user is None:
        raise HTTPException(status_code=401, detail="Login with Telegram or TON wallet.")
    return user


def user_for_generation(user: User | None = Depends(get_optional_user)) -> User | None:
    if auth_required() and user is None:
        raise HTTPException(status_code=401, detail="Login with Telegram or TON wallet to generate.")
    return user
