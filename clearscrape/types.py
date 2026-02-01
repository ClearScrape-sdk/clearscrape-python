"""Type definitions for the ClearScrape SDK."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Literal


DomainType = Literal[
    "amazon",
    "walmart",
    "google",
    "google_shopping",
    "ebay",
    "target",
    "etsy",
    "bestbuy",
    "homedepot",
    "zillow",
    "yelp",
    "indeed",
    "linkedin_jobs",
]


@dataclass
class ScrapeOptions:
    """Options for scraping requests."""

    url: str
    method: str = "GET"
    js_render: bool = False
    premium_proxy: bool = False
    antibot: bool = False
    proxy_country: Optional[str] = None
    wait_for: Optional[str] = None
    wait: Optional[int] = None
    auto_scroll: bool = False
    screenshot: bool = False
    screenshot_selector: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None
    domain: Optional[DomainType] = None


@dataclass
class ScrapeResponse:
    """Response from a scraping request."""

    success: bool
    html: str
    text: Optional[str] = None
    screenshot: Optional[str] = None
    extracted: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    credits_used: int = 1
    url: Optional[str] = None
    status_code: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScrapeResponse":
        """Create a ScrapeResponse from a dictionary."""
        return cls(
            success=data.get("success", True),
            html=data.get("data", {}).get("html", ""),
            text=data.get("data", {}).get("text"),
            screenshot=data.get("data", {}).get("screenshot"),
            extracted=data.get("data", {}).get("extracted"),
            metadata=data.get("data", {}).get("metadata"),
            credits_used=data.get("credits_used", 1),
            url=data.get("data", {}).get("url"),
            status_code=data.get("data", {}).get("status_code"),
        )


@dataclass
class ProxyConfig:
    """Proxy configuration for residential proxy service."""

    host: str = "proxy.clearscrape.io"
    port: int = 8000
    username: str = ""
    password: str = ""

    @property
    def url(self) -> str:
        """Get the full proxy URL."""
        return f"http://{self.username}:{self.password}@{self.host}:{self.port}"

    def as_dict(self) -> Dict[str, Any]:
        """Get proxy config as a dictionary for requests library."""
        proxy_url = self.url
        return {
            "http": proxy_url,
            "https": proxy_url,
        }
