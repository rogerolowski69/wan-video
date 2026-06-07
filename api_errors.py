"""User-friendly messages for common API billing and auth failures."""

from __future__ import annotations

import re
import sys
from collections.abc import Callable


class ApiBillingError(RuntimeError):
    """Raised for known provider billing/auth failures (message is user-facing)."""


def _extract_fal_reason(message: str) -> str | None:
    match = re.search(r"Reason:\s*(.+?)(?:\.\s*Top up|$)", message, re.IGNORECASE)
    return match.group(1).strip() if match else None


def format_api_error(exc: BaseException) -> str:
    """Return a short, actionable error string for known provider failures."""
    text = str(exc)
    lower = text.lower()

    if "exhausted balance" in lower or "user is locked" in lower:
        reason = _extract_fal_reason(text) or "exhausted balance"
        return f"fal.ai: {reason}. Top up at https://fal.ai/dashboard/billing"

    if "402 payment required" in lower or "depleted your monthly included credits" in lower:
        return (
            "Hugging Face Inference Providers: monthly credits depleted. "
            "Add credits at https://huggingface.co/settings/billing"
        )

    if "403 forbidden" in lower and "fal" in lower:
        return f"fal.ai request denied: {text}"

    if "401" in lower or "unauthorized" in lower:
        return f"Authentication failed — check HF_TOKEN / FAL_KEY in .env: {text}"

    return text


def exit_on_api_error(exc: BaseException) -> None:
    """Raise ApiBillingError with a clean, actionable message."""
    raise ApiBillingError(format_api_error(exc)) from None


def run_cli(main: Callable[[], None]) -> None:
    """Entry-point wrapper — prints billing errors without a traceback."""
    try:
        main()
    except ApiBillingError as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        sys.exit(1)
