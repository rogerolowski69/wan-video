"""Add project root to sys.path so scripts can import shared modules."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def install() -> None:
    root = str(ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
