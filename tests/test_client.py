"""Tests for the Yahoo HTTP client."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import httpx
import pytest

from yoghurt.client import YahooClient
from yoghurt.exceptions import YahooRequestError
from yoghurt.session_cache import save_session_cache

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_httpx import HTTPXMock

REQUEST_ATTEMPTS = 3


@pytest.mark.asyncio
async def test_get_redacts_crumb_from_request_error(
    httpx_mock: HTTPXMock,
    tmp_path: Path,
) -> None:
    """Failed API requests do not expose Yahoo crumbs in user-facing errors."""

    cache_path = tmp_path / "session.json"
    cookies = httpx.Cookies()
    cookies.set("A3", "token", domain=".yahoo.com", path="/")
    save_session_cache(cache_path, cookies, "secret-crumb", time.time() + 3600)
    httpx_mock.add_response(
        method="GET",
        url="https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL&crumb=secret-crumb",
        status_code=404,
        json={"finance": {"error": {"code": "Not Found"}}},
    )
    client = YahooClient(session_cache_path=cache_path)

    try:
        with pytest.raises(YahooRequestError) as exc_info:
            await client.get("/v7/finance/quote", {"symbols": "AAPL"})
    finally:
        await client.aclose()

    assert "secret-crumb" not in str(exc_info.value)
    assert "crumb=" not in str(exc_info.value)
    assert "symbols=AAPL" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_retries_retryable_status_codes(
    httpx_mock: HTTPXMock,
    tmp_path: Path,
) -> None:
    """Retryable GET failures are retried before surfacing the final response."""

    cache_path = tmp_path / "session.json"
    cookies = httpx.Cookies()
    cookies.set("A3", "token", domain=".yahoo.com", path="/")
    save_session_cache(cache_path, cookies, "crumb-token", time.time() + 3600)
    url = (
        "https://query1.finance.yahoo.com/v7/finance/quote?"
        "symbols=AAPL&crumb=crumb-token"
    )
    httpx_mock.add_response(method="GET", url=url, status_code=503)
    httpx_mock.add_response(method="GET", url=url, status_code=503)
    httpx_mock.add_response(method="GET", url=url, text='{"ok":true}')
    client = YahooClient(session_cache_path=cache_path)

    try:
        body = await client.get("/v7/finance/quote", {"symbols": "AAPL"})
    finally:
        await client.aclose()

    assert body == '{"ok":true}'
    assert len(httpx_mock.get_requests()) == REQUEST_ATTEMPTS


@pytest.mark.asyncio
async def test_get_uses_cached_session_without_refreshing(
    httpx_mock: HTTPXMock,
    tmp_path: Path,
) -> None:
    """A valid cached cookie and crumb are enough for a one-shot API call."""

    cache_path = tmp_path / "session.json"
    cookies = httpx.Cookies()
    cookies.set("A3", "token", domain=".yahoo.com", path="/")
    save_session_cache(cache_path, cookies, "crumb-token", time.time() + 3600)
    httpx_mock.add_response(
        method="GET",
        url=(
            "https://query1.finance.yahoo.com/v7/finance/quote?"
            "symbols=AAPL&crumb=crumb-token"
        ),
        text='{"ok":true}',
    )
    client = YahooClient(session_cache_path=cache_path)

    try:
        body = await client.get("/v7/finance/quote", {"symbols": "AAPL"})
    finally:
        await client.aclose()

    assert body == '{"ok":true}'
    assert [request.url.host for request in httpx_mock.get_requests()] == [
        "query1.finance.yahoo.com"
    ]
