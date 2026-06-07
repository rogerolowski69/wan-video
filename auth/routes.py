"""Auth API routes — Telegram Mini App and TON wallet login."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth.deps import auth_required, get_optional_user, require_user
from auth.jwt_utils import create_access_token
from auth.telegram_auth import TelegramAuthError, bot_token, validate_init_data
from auth.users import link_wallet, upsert_telegram_user, upsert_wallet_user, user_payload
from db.models import User
from db.session import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


class TelegramAuthRequest(BaseModel):
    init_data: str = Field(description="Raw Telegram.WebApp.initData string")


class TonAuthRequest(BaseModel):
    wallet_address: str = Field(min_length=10, max_length=128)


class LinkWalletRequest(BaseModel):
    wallet_address: str = Field(min_length=10, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict[str, object]


@router.get("/config")
def auth_config() -> dict[str, object]:
    return {
        "auth_required": auth_required(),
        "telegram_enabled": bot_token() is not None,
        "ton_enabled": True,
    }


@router.post("/telegram", response_model=AuthResponse)
def login_telegram(body: TelegramAuthRequest) -> AuthResponse:
    try:
        tg_user = validate_init_data(body.init_data)
    except TelegramAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    session = get_session()
    try:
        user = upsert_telegram_user(session, tg_user)
    finally:
        session.close()

    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=user_payload(user))


@router.post("/ton", response_model=AuthResponse)
def login_ton(body: TonAuthRequest) -> AuthResponse:
    session = get_session()
    try:
        user = upsert_wallet_user(session, body.wallet_address)
    finally:
        session.close()

    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=user_payload(user))


@router.post("/ton/link", response_model=AuthResponse)
def link_ton_wallet(
    body: LinkWalletRequest,
    user: User = Depends(require_user),
) -> AuthResponse:
    session = get_session()
    try:
        db_user = session.get(User, user.id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            updated = link_wallet(session, db_user, body.wallet_address)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
    finally:
        session.close()

    token = create_access_token(updated.id)
    return AuthResponse(access_token=token, user=user_payload(updated))


@router.get("/me")
def me(user: User | None = Depends(get_optional_user)) -> dict[str, object]:
    if user is None:
        return {"authenticated": False, "auth_required": auth_required()}
    return {"authenticated": True, "auth_required": auth_required(), "user": user_payload(user)}
