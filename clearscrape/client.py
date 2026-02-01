"""Main ClearScrape client implementation."""

import time
from typing import Optional, Dict, Any, TypeVar, Type
from urllib.parse import urlencode

import httpx

from .exceptions import (
    ClearScrapeError,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    TimeoutError,
)
from .types import ScrapeOptions, ScrapeResponse, ProxyConfig, DomainType

T = TypeVar("T")

DEFAULT_BASE_URL = "https://api.clearscrape.io"
DEFAULT_TIMEOUT = 60.0
DEFAULT_RETRIES = 3


class ClearScrape:
    """
    ClearScrape API Client.

    A Python client for the ClearScrape web scraping API.

    Args:
        api_key: Your ClearScrape API key
        base_url: Custom API base URL (default: https://api.clearscrape.io)
        timeout: Request timeout in seconds (default: 60)
        retries: Number of retries for failed requests (default: 3)

    Example:
        >>> from clearscrape import ClearScrape
        >>>
        >>> client = ClearScrape(api_key="your-api-key")
        >>>
        >>> # Simple scrape
        >>> result = client.scrape("https://example.com")
        >>> print(result.html)
        >>>
        >>> # With JavaScript rendering
        >>> result = client.scrape(
        ...     "https://example.com",
        ...     js_render=True,
        ...     wait_for=".content"
        ... )
        >>>
        >>> # Extract Amazon product data
        >>> product = client.extract(
        ...     "https://www.amazon.com/dp/B09V3KXJPB",
        ...     domain="amazon"
        ... )
        >>> print(product["title"], product["price"])
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ):
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries

        self._client = httpx.Client(
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json",
            },
        )

    def __enter__(self) -> "ClearScrape":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def scrape(
        self,
        url: str,
        *,
        method: str = "GET",
        js_render: bool = False,
        premium_proxy: bool = False,
        antibot: bool = False,
        proxy_country: Optional[str] = None,
        wait_for: Optional[str] = None,
        wait: Optional[int] = None,
        auto_scroll: bool = False,
        screenshot: bool = False,
        screenshot_selector: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        domain: Optional[DomainType] = None,
    ) -> ScrapeResponse:
        """
        Scrape a URL and return the HTML content.

        Args:
            url: Target URL to scrape
            method: HTTP method (default: GET)
            js_render: Enable JavaScript rendering (+5 credits)
            premium_proxy: Use residential proxy (+10 credits)
            antibot: Enable antibot bypass (+25 credits)
            proxy_country: Two-letter country code for geo-targeting
            wait_for: CSS selector to wait for before returning
            wait: Additional wait time in milliseconds
            auto_scroll: Scroll page to load lazy content
            screenshot: Capture a screenshot
            screenshot_selector: CSS selector for screenshot element
            headers: Custom HTTP headers
            body: Request body for POST requests
            domain: Domain extractor (amazon, walmart, google, etc.)

        Returns:
            ScrapeResponse with HTML content and metadata

        Example:
            >>> result = client.scrape(
            ...     "https://example.com",
            ...     js_render=True,
            ...     wait_for=".content"
            ... )
            >>> print(result.html)
        """
        payload: Dict[str, Any] = {"url": url}

        if method != "GET":
            payload["method"] = method
        if js_render:
            payload["js_render"] = True
        if premium_proxy:
            payload["premium_proxy"] = True
        if antibot:
            payload["antibot"] = True
        if proxy_country:
            payload["proxy_country"] = proxy_country
        if wait_for:
            payload["wait_for"] = wait_for
        if wait:
            payload["wait"] = wait
        if auto_scroll:
            payload["auto_scroll"] = True
        if screenshot:
            payload["screenshot"] = True
        if screenshot_selector:
            payload["screenshot_selector"] = screenshot_selector
        if headers:
            payload["headers"] = headers
        if body:
            payload["body"] = body
        if domain:
            payload["domain"] = domain

        data = self._make_request("/api/scrape", payload)
        return ScrapeResponse.from_dict(data)

    def get_html(
        self,
        url: str,
        **kwargs,
    ) -> str:
        """
        Scrape a URL and return only the HTML content.

        Args:
            url: Target URL to scrape
            **kwargs: Additional options passed to scrape()

        Returns:
            HTML content as a string
        """
        result = self.scrape(url, **kwargs)
        return result.html

    def get_text(
        self,
        url: str,
        **kwargs,
    ) -> str:
        """
        Scrape a URL and return only the text content.

        Args:
            url: Target URL to scrape
            **kwargs: Additional options passed to scrape()

        Returns:
            Text content as a string
        """
        result = self.scrape(url, **kwargs)
        return result.text or ""

    def screenshot(
        self,
        url: str,
        *,
        selector: Optional[str] = None,
        **kwargs,
    ) -> bytes:
        """
        Capture a screenshot of a URL.

        Args:
            url: Target URL to screenshot
            selector: CSS selector to screenshot specific element
            **kwargs: Additional options passed to scrape()

        Returns:
            Screenshot as bytes (PNG format)

        Example:
            >>> screenshot = client.screenshot("https://example.com")
            >>> with open("screenshot.png", "wb") as f:
            ...     f.write(screenshot)
        """
        import base64

        result = self.scrape(
            url,
            js_render=True,
            screenshot=True,
            screenshot_selector=selector,
            **kwargs,
        )

        if not result.screenshot:
            raise ClearScrapeError("Screenshot not returned")

        # Remove data URL prefix if present
        screenshot_data = result.screenshot
        if screenshot_data.startswith("data:"):
            screenshot_data = screenshot_data.split(",", 1)[1]

        return base64.b64decode(screenshot_data)

    def extract(
        self,
        url: str,
        domain: DomainType,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Extract structured data using domain-specific extractors.

        Args:
            url: Target URL to extract data from
            domain: Domain extractor to use (amazon, walmart, google, etc.)
            **kwargs: Additional options passed to scrape()

        Returns:
            Extracted data as a dictionary

        Example:
            >>> # Extract Amazon product data
            >>> product = client.extract(
            ...     "https://www.amazon.com/dp/B09V3KXJPB",
            ...     domain="amazon"
            ... )
            >>> print(product["title"])
            >>> print(product["price"])
            >>>
            >>> # Extract Google SERP data
            >>> serp = client.extract(
            ...     "https://www.google.com/search?q=best+laptops",
            ...     domain="google"
            ... )
            >>> print(serp["organic_results"])
        """
        result = self.scrape(url, domain=domain, **kwargs)

        if not result.extracted:
            raise ClearScrapeError("No extracted data returned")

        return result.extracted

    def get_proxy_config(
        self,
        *,
        country: Optional[str] = None,
        session: Optional[str] = None,
    ) -> ProxyConfig:
        """
        Get proxy configuration for the residential proxy service.

        Args:
            country: Two-letter country code for geo-targeting
            session: Session ID for sticky IP sessions

        Returns:
            ProxyConfig object with host, port, username, password

        Example:
            >>> proxy = client.get_proxy_config(country="us")
            >>> print(proxy.url)
            >>> # Use with requests
            >>> import requests
            >>> response = requests.get(
            ...     "https://httpbin.org/ip",
            ...     proxies=proxy.as_dict()
            ... )
        """
        username = self.api_key

        if country:
            username += f"-country-{country}"
        if session:
            username += f"-session-{session}"

        return ProxyConfig(
            host="proxy.clearscrape.io",
            port=8000,
            username=username,
            password=self.api_key,
        )

    def get_proxy_url(
        self,
        *,
        country: Optional[str] = None,
        session: Optional[str] = None,
    ) -> str:
        """
        Get proxy URL string for use with HTTP clients.

        Args:
            country: Two-letter country code for geo-targeting
            session: Session ID for sticky IP sessions

        Returns:
            Proxy URL string

        Example:
            >>> proxy_url = client.get_proxy_url(country="us")
            >>> # Use with httpx
            >>> import httpx
            >>> response = httpx.get(
            ...     "https://httpbin.org/ip",
            ...     proxies=proxy_url
            ... )
        """
        config = self.get_proxy_config(country=country, session=session)
        return config.url

    def get_browser_ws_url(
        self,
        *,
        proxy_country: Optional[str] = None,
    ) -> str:
        """
        Get WebSocket URL for Scraping Browser (Playwright/Puppeteer).

        Args:
            proxy_country: Two-letter country code for geo-targeting

        Returns:
            WebSocket URL for browser connection

        Example:
            >>> # Use with Playwright
            >>> from playwright.sync_api import sync_playwright
            >>>
            >>> ws_url = client.get_browser_ws_url()
            >>> with sync_playwright() as p:
            ...     browser = p.chromium.connect_over_cdp(ws_url)
            ...     page = browser.new_page()
            ...     page.goto("https://example.com")
            ...     print(page.title())
            ...     browser.close()
        """
        params = {"apiKey": self.api_key}

        if proxy_country:
            params["proxy_country"] = proxy_country

        return f"wss://browser.clearscrape.io?{urlencode(params)}"

    def _make_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        attempt: int = 1,
    ) -> Dict[str, Any]:
        """Make an API request with retries."""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self._client.post(url, json=payload)
            data = response.json()

            if not response.is_success:
                return self._handle_error(
                    response.status_code,
                    data,
                    payload,
                    attempt,
                )

            return data

        except httpx.TimeoutException:
            if attempt < self.retries:
                time.sleep(2**attempt)
                return self._make_request(endpoint, payload, attempt + 1)
            raise TimeoutError()

        except httpx.RequestError as e:
            if attempt < self.retries:
                time.sleep(2**attempt)
                return self._make_request(endpoint, payload, attempt + 1)
            raise ClearScrapeError(str(e))

    def _handle_error(
        self,
        status_code: int,
        response: Dict[str, Any],
        payload: Dict[str, Any],
        attempt: int,
    ) -> Dict[str, Any]:
        """Handle API errors with appropriate exceptions."""
        message = response.get("message") or response.get("error", "Unknown error")

        # Don't retry client errors (except rate limits)
        if 400 <= status_code < 500 and status_code != 429:
            if status_code == 401:
                raise AuthenticationError(message)
            if status_code == 402:
                raise InsufficientCreditsError(
                    message,
                    required=response.get("required"),
                )
            raise ClearScrapeError(message, status_code, response)

        # Retry rate limits and server errors
        if attempt < self.retries:
            delay = 5 if status_code == 429 else 2**attempt
            time.sleep(delay)
            return self._make_request("/api/scrape", payload, attempt + 1)

        if status_code == 429:
            raise RateLimitError(message)

        raise ClearScrapeError(message, status_code, response)


class AsyncClearScrape:
    """
    Async ClearScrape API Client.

    An async Python client for the ClearScrape web scraping API.

    Example:
        >>> import asyncio
        >>> from clearscrape import AsyncClearScrape
        >>>
        >>> async def main():
        ...     async with AsyncClearScrape(api_key="your-api-key") as client:
        ...         result = await client.scrape("https://example.com")
        ...         print(result.html)
        >>>
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ):
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries

        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json",
            },
        )

    async def __aenter__(self) -> "AsyncClearScrape":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def scrape(
        self,
        url: str,
        *,
        method: str = "GET",
        js_render: bool = False,
        premium_proxy: bool = False,
        antibot: bool = False,
        proxy_country: Optional[str] = None,
        wait_for: Optional[str] = None,
        wait: Optional[int] = None,
        auto_scroll: bool = False,
        screenshot: bool = False,
        screenshot_selector: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        domain: Optional[DomainType] = None,
    ) -> ScrapeResponse:
        """Async version of scrape(). See ClearScrape.scrape() for details."""
        payload: Dict[str, Any] = {"url": url}

        if method != "GET":
            payload["method"] = method
        if js_render:
            payload["js_render"] = True
        if premium_proxy:
            payload["premium_proxy"] = True
        if antibot:
            payload["antibot"] = True
        if proxy_country:
            payload["proxy_country"] = proxy_country
        if wait_for:
            payload["wait_for"] = wait_for
        if wait:
            payload["wait"] = wait
        if auto_scroll:
            payload["auto_scroll"] = True
        if screenshot:
            payload["screenshot"] = True
        if screenshot_selector:
            payload["screenshot_selector"] = screenshot_selector
        if headers:
            payload["headers"] = headers
        if body:
            payload["body"] = body
        if domain:
            payload["domain"] = domain

        data = await self._make_request("/api/scrape", payload)
        return ScrapeResponse.from_dict(data)

    async def get_html(self, url: str, **kwargs) -> str:
        """Async version of get_html()."""
        result = await self.scrape(url, **kwargs)
        return result.html

    async def get_text(self, url: str, **kwargs) -> str:
        """Async version of get_text()."""
        result = await self.scrape(url, **kwargs)
        return result.text or ""

    async def screenshot(
        self,
        url: str,
        *,
        selector: Optional[str] = None,
        **kwargs,
    ) -> bytes:
        """Async version of screenshot()."""
        import base64

        result = await self.scrape(
            url,
            js_render=True,
            screenshot=True,
            screenshot_selector=selector,
            **kwargs,
        )

        if not result.screenshot:
            raise ClearScrapeError("Screenshot not returned")

        screenshot_data = result.screenshot
        if screenshot_data.startswith("data:"):
            screenshot_data = screenshot_data.split(",", 1)[1]

        return base64.b64decode(screenshot_data)

    async def extract(
        self,
        url: str,
        domain: DomainType,
        **kwargs,
    ) -> Dict[str, Any]:
        """Async version of extract()."""
        result = await self.scrape(url, domain=domain, **kwargs)

        if not result.extracted:
            raise ClearScrapeError("No extracted data returned")

        return result.extracted

    def get_proxy_config(
        self,
        *,
        country: Optional[str] = None,
        session: Optional[str] = None,
    ) -> ProxyConfig:
        """Get proxy configuration. See ClearScrape.get_proxy_config()."""
        username = self.api_key

        if country:
            username += f"-country-{country}"
        if session:
            username += f"-session-{session}"

        return ProxyConfig(
            host="proxy.clearscrape.io",
            port=8000,
            username=username,
            password=self.api_key,
        )

    def get_proxy_url(
        self,
        *,
        country: Optional[str] = None,
        session: Optional[str] = None,
    ) -> str:
        """Get proxy URL. See ClearScrape.get_proxy_url()."""
        config = self.get_proxy_config(country=country, session=session)
        return config.url

    def get_browser_ws_url(
        self,
        *,
        proxy_country: Optional[str] = None,
    ) -> str:
        """Get browser WebSocket URL. See ClearScrape.get_browser_ws_url()."""
        params = {"apiKey": self.api_key}

        if proxy_country:
            params["proxy_country"] = proxy_country

        return f"wss://browser.clearscrape.io?{urlencode(params)}"

    async def _make_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        attempt: int = 1,
    ) -> Dict[str, Any]:
        """Make an async API request with retries."""
        import asyncio

        url = f"{self.base_url}{endpoint}"

        try:
            response = await self._client.post(url, json=payload)
            data = response.json()

            if not response.is_success:
                return await self._handle_error(
                    response.status_code,
                    data,
                    payload,
                    attempt,
                )

            return data

        except httpx.TimeoutException:
            if attempt < self.retries:
                await asyncio.sleep(2**attempt)
                return await self._make_request(endpoint, payload, attempt + 1)
            raise TimeoutError()

        except httpx.RequestError as e:
            if attempt < self.retries:
                await asyncio.sleep(2**attempt)
                return await self._make_request(endpoint, payload, attempt + 1)
            raise ClearScrapeError(str(e))

    async def _handle_error(
        self,
        status_code: int,
        response: Dict[str, Any],
        payload: Dict[str, Any],
        attempt: int,
    ) -> Dict[str, Any]:
        """Handle API errors with appropriate exceptions."""
        import asyncio

        message = response.get("message") or response.get("error", "Unknown error")

        if 400 <= status_code < 500 and status_code != 429:
            if status_code == 401:
                raise AuthenticationError(message)
            if status_code == 402:
                raise InsufficientCreditsError(
                    message,
                    required=response.get("required"),
                )
            raise ClearScrapeError(message, status_code, response)

        if attempt < self.retries:
            delay = 5 if status_code == 429 else 2**attempt
            await asyncio.sleep(delay)
            return await self._make_request("/api/scrape", payload, attempt + 1)

        if status_code == 429:
            raise RateLimitError(message)

        raise ClearScrapeError(message, status_code, response)
