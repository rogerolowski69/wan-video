"""User lookup and upsert helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import User


def _touch(user: User) -> None:
    user.last_login_at = datetime.now(timezone.utc)


def upsert_telegram_user(session: Session, tg_user: dict[str, Any]) -> User:
    telegram_id = int(tg_user["id"])
    existing = session.scalars(select(User).where(User.telegram_id == telegram_id)).first()
    if existing is None:
        existing = User(telegram_id=telegram_id)
        session.add(existing)

    existing.username = tg_user.get("username")
    existing.display_name = _display_name(tg_user)
    existing.photo_url = tg_user.get("photo_url")
    _touch(existing)
    session.commit()
    session.refresh(existing)
    return existing


def upsert_wallet_user(session: Session, wallet_address: str) -> User:
    normalized = wallet_address.strip()
    existing = session.scalars(select(User).where(User.wallet_address == normalized)).first()
    if existing is None:
        existing = User(wallet_address=normalized)
        session.add(existing)
    _touch(existing)
    session.commit()
    session.refresh(existing)
    return existing


def link_wallet(session: Session, user: User, wallet_address: str) -> User:
    normalized = wallet_address.strip()
    other = session.scalars(
        select(User).where(User.wallet_address == normalized, User.id != user.id)
    ).first()
    if other is not None:
        raise ValueError("Wallet already linked to another account")

    user.wallet_address = normalized
    _touch(user)
    session.commit()
    session.refresh(user)
    return user


def user_payload(user: User) -> dict[str, object]:
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "wallet_address": user.wallet_address,
        "username": user.username,
        "display_name": user.display_name,
        "photo_url": user.photo_url,
    }


def _display_name(tg_user: dict[str, Any]) -> str | None:
    parts = [tg_user.get("first_name"), tg_user.get("last_name")]
    name = " ".join(part for part in parts if part).strip()
    return name or tg_user.get("username")
