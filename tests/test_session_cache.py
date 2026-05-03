"""Tests for Yahoo session-cache persistence."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import httpx

from yogurt.session_cache import load_session_cache, save_session_cache

if TYPE_CHECKING:
    from pathlib import Path


def test_session_cache_round_trips_cookies_crumb_and_expiry(tmp_path: Path) -> None:
    """Session cache preserves the data needed for one-shot CLI reuse."""

    path = tmp_path / "session.json"
    cookies = httpx.Cookies()
    expiry = time.time() + 3600
    cookies.set("A3", "token", domain=".yahoo.com", path="/")

    save_session_cache(path, cookies, "crumb-token", expiry)
    loaded = load_session_cache(path)

    assert loaded is not None
    assert loaded.crumb == "crumb-token"
    assert loaded.expiry == expiry
    assert loaded.cookies.get("A3") == "token"
    assert loaded.is_valid
