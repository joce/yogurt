"""Yogurt-specific exception hierarchy."""

from __future__ import annotations


class YogurtError(Exception):
    """Base exception for all Yogurt errors."""


class YahooRequestError(YogurtError):
    """Raised when Yahoo rejects an HTTP request."""

    def __init__(
        self,
        status_code: int,
        url: str,
        *,
        reason: str | None = None,
    ) -> None:
        """Initialize the request error."""

        message = f"Yahoo request rejected with HTTP {status_code} for {url}"
        if reason:
            message = f"{message}: {reason}"
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.reason = reason


class YahooUnavailableError(YogurtError):
    """Raised when Yahoo cannot be reached due to transport failure."""

    def __init__(self, context: str) -> None:
        """Initialize the transport error."""

        super().__init__(f"Yahoo Finance unavailable while processing {context}")
        self.context = context
