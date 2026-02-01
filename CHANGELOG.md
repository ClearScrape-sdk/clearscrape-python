# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-02-01

### Added

- Initial release of ClearScrape Node.js SDK
- Core `ClearScrape` client class with full API support
- `scrape()` - Full scraping with all options
- `getHtml()` - Quick HTML extraction
- `getText()` - Quick text extraction
- `screenshot()` - Page screenshots
- `extract()` - Domain-specific data extraction (Amazon, Walmart, Google, etc.)
- `getProxyConfig()` - Residential proxy configuration
- `getProxyUrl()` - Proxy URL string for HTTP clients
- `getBrowserWsUrl()` - WebSocket URL for Playwright/Puppeteer
- Full TypeScript support with comprehensive type definitions
- Automatic retries with exponential backoff
- Error classes: `ClearScrapeError`, `InsufficientCreditsError`, `RateLimitError`
- Support for all ClearScrape features:
  - JavaScript rendering
  - Premium residential proxies
  - Antibot bypass (Cloudflare, DataDome, PerimeterX)
  - Screenshots (full page and selector-based)
  - Domain extractors (Amazon, Walmart, Google, eBay, etc.)
  - Country targeting for proxies
  - Wait for selector/timeout
  - Auto-scroll for lazy-loaded content
