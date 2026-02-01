# ClearScrape Python SDK

Official Python client for the [ClearScrape](https://clearscrape.io) web scraping API.

## Features

- Simple, intuitive API
- Full async/await support
- Type hints throughout
- Automatic retries with exponential backoff
- Support for all ClearScrape features:
  - JavaScript rendering
  - Premium residential proxies
  - Antibot bypass
  - Screenshots
  - Domain-specific extractors (Amazon, Walmart, Google, etc.)
  - Scraping Browser (Playwright/Puppeteer)
  - Residential Proxy service

## Installation

```bash
pip install clearscrape
```

## Quick Start

```python
from clearscrape import ClearScrape

client = ClearScrape(api_key="your-api-key")

# Basic scrape
result = client.scrape("https://example.com")
print(result.html)
```

## Usage Examples

### Basic Scraping

```python
# Simple HTML fetch
result = client.scrape("https://example.com")

# Get just the HTML
html = client.get_html("https://example.com")

# Get just the text content
text = client.get_text("https://example.com")
```

### JavaScript Rendering

Enable JavaScript rendering for dynamic websites (SPAs, React, Vue, etc.):

```python
result = client.scrape(
    "https://example.com/spa-page",
    js_render=True,
    wait_for=".product-list",  # Wait for element
    wait=3000                   # Additional wait time (ms)
)
```

### Premium Proxies

Use residential proxies to avoid blocks and geo-target:

```python
result = client.scrape(
    "https://example.com",
    premium_proxy=True,
    proxy_country="us"  # Target specific country
)
```

### Antibot Bypass

Bypass Cloudflare, DataDome, PerimeterX and other bot protection:

```python
result = client.scrape(
    "https://protected-site.com",
    antibot=True,
    premium_proxy=True
)
```

### Screenshots

Capture screenshots of web pages:

```python
# Get screenshot as bytes
screenshot = client.screenshot("https://example.com")

# Save to file
with open("screenshot.png", "wb") as f:
    f.write(screenshot)

# Screenshot specific element
screenshot = client.screenshot(
    "https://example.com",
    selector=".product-card"
)
```

### Domain Extractors

Extract structured data from supported websites:

```python
# Amazon product data
product = client.extract(
    "https://www.amazon.com/dp/B09V3KXJPB",
    domain="amazon"
)

print(product["title"])       # "Apple AirPods Pro..."
print(product["price"])       # "$249.00"
print(product["rating"])      # "4.7"
print(product["review_count"]) # "125,432"

# Google SERP data
serp = client.extract(
    "https://www.google.com/search?q=best+laptops",
    domain="google"
)

print(serp["organic_results"][0]["title"])
print(serp["featured_snippet"])
print(serp["related_searches"])
```

**Supported domains:**
- `amazon` - Product pages
- `walmart` - Product pages
- `google` - Search results
- `google_shopping` - Shopping results
- `ebay` - Product pages
- `target` - Product pages
- `etsy` - Product pages
- `bestbuy` - Product pages
- `homedepot` - Product pages
- `zillow` - Property listings
- `yelp` - Business pages
- `indeed` - Job listings
- `linkedin_jobs` - Job listings

### Scraping Browser (Playwright/Puppeteer)

Connect to cloud browsers with built-in antibot bypass:

```python
# With Playwright
from playwright.sync_api import sync_playwright

ws_url = client.get_browser_ws_url()

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(ws_url)
    page = browser.new_page()
    page.goto("https://example.com")

    title = page.title()
    browser.close()
```

```python
# With country targeting
ws_url = client.get_browser_ws_url(proxy_country="gb")
```

### Residential Proxies

Use ClearScrape proxies with any HTTP client:

```python
# Get proxy configuration
proxy = client.get_proxy_config()
# ProxyConfig(host='proxy.clearscrape.io', port=8000, username='...', password='...')

# Get proxy URL string
proxy_url = client.get_proxy_url()
# 'http://apikey:apikey@proxy.clearscrape.io:8000'

# With country targeting
proxy_url = client.get_proxy_url(country="us")

# With session sticky IP
proxy_url = client.get_proxy_url(session="my-session-123")

# Combined
proxy_url = client.get_proxy_url(country="us", session="abc")
```

**Use with requests:**
```python
import requests

proxy = client.get_proxy_config(country="us")
response = requests.get(
    "https://httpbin.org/ip",
    proxies=proxy.as_dict()
)
```

**Use with httpx:**
```python
import httpx

proxy_url = client.get_proxy_url()
response = httpx.get(
    "https://httpbin.org/ip",
    proxies=proxy_url
)
```

### Async Usage

For async applications, use `AsyncClearScrape`:

```python
import asyncio
from clearscrape import AsyncClearScrape

async def main():
    async with AsyncClearScrape(api_key="your-api-key") as client:
        # All methods are async
        result = await client.scrape("https://example.com")
        print(result.html)

        # Scrape multiple URLs concurrently
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
        ]
        results = await asyncio.gather(*[
            client.scrape(url) for url in urls
        ])

asyncio.run(main())
```

## Configuration

```python
client = ClearScrape(
    # Required: Your API key
    api_key="your-api-key",

    # Optional: Custom base URL (default: https://api.clearscrape.io)
    base_url="https://api.clearscrape.io",

    # Optional: Request timeout in seconds (default: 60)
    timeout=60,

    # Optional: Number of retries (default: 3)
    retries=3
)
```

## Error Handling

```python
from clearscrape import (
    ClearScrape,
    ClearScrapeError,
    InsufficientCreditsError,
    RateLimitError,
    AuthenticationError,
)

try:
    result = client.scrape("https://example.com")
except AuthenticationError:
    print("Invalid API key")
except InsufficientCreditsError as e:
    print(f"Need {e.required} credits")
except RateLimitError:
    print("Rate limited, try again later")
except ClearScrapeError as e:
    print(f"Error {e.status_code}: {e.message}")
```

## Credits

| Feature | Cost |
|---------|------|
| Base request | 1 credit |
| + JavaScript rendering | +5 credits |
| + Premium proxy | +10 credits |
| + Antibot bypass | +25 credits |
| Domain API extraction | 25 credits |

## Support

- [Documentation](https://clearscrape.io/docs)
- [API Reference](https://clearscrape.io/docs#parameters)
- [GitHub Issues](https://github.com/ClearScrape-sdk/clearscrape-python/issues)

## License

MIT
