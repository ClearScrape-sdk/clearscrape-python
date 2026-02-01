"""Custom exceptions for the ClearScrape SDK."""

from typing import Optional, Dict, Any


class ClearScrapeError(Exception):
    """Base exception for all ClearScrape errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(ClearScrapeError):
    """Raised when API key is invalid or missing."""

    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message, status_code=401)


class InsufficientCreditsError(ClearScrapeError):
    """Raised when account has insufficient credits."""

    def __init__(
        self,
        message: str = "Insufficient credits",
        required: Optional[int] = None,
    ):
        super().__init__(message, status_code=402)
        self.required = required


class RateLimitError(ClearScrapeError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class TimeoutError(ClearScrapeError):
    """Raised when request times out."""

    def __init__(self, message: str = "Request timed out"):
        super().__init__(message, status_code=408)
