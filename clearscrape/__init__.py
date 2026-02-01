"""
ClearScrape Python SDK

Official Python client for the ClearScrape web scraping API.

Example:
    >>> from clearscrape import ClearScrape
    >>> client = ClearScrape(api_key="your-api-key")
    >>> result = client.scrape("https://example.com")
    >>> print(result.html)
"""

from .client import ClearScrape
from .exceptions import (
    ClearScrapeError,
    InsufficientCreditsError,
    RateLimitError,
    AuthenticationError,
    TimeoutError,
)
from .types import (
    ScrapeOptions,
    ScrapeResponse,
    ProxyConfig,
)

__version__ = "1.0.0"
__all__ = [
    "ClearScrape",
    "ClearScrapeError",
    "InsufficientCreditsError",
    "RateLimitError",
    "AuthenticationError",
    "TimeoutError",
    "ScrapeOptions",
    "ScrapeResponse",
    "ProxyConfig",
]
