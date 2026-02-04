# ClearScrape Node.js SDK

Official Node.js client for the [ClearScrape](https://clearscrape.io) web scraping API.

## Features

- Simple, promise-based API
- Full TypeScript support
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
npm install clearscrape
```

```bash
yarn add clearscrape
```

```bash
pnpm add clearscrape
```

## Quick Start

```typescript
import { ClearScrape } from 'clearscrape';

const client = new ClearScrape({
  apiKey: process.env.CLEARSCRAPE_API_KEY
});

// Basic scrape
const result = await client.scrape({
  url: 'https://example.com'
});

console.log(result.data.html);
```

## Usage Examples

### Basic Scraping

```typescript
// Simple HTML fetch
const result = await client.scrape({
  url: 'https://example.com'
});

// Get just the HTML
const html = await client.getHtml('https://example.com');

// Get just the text content
const text = await client.getText('https://example.com');
```

### JavaScript Rendering

Enable JavaScript rendering for dynamic websites (SPAs, React, Vue, etc.):

```typescript
const result = await client.scrape({
  url: 'https://example.com/spa-page',
  jsRender: true,
  waitFor: '.product-list',  // Wait for element
  wait: 3000                  // Additional wait time (ms)
});
```

### Premium Proxies

Use residential proxies to avoid blocks and geo-target:

```typescript
const result = await client.scrape({
  url: 'https://example.com',
  premiumProxy: true,
  proxyCountry: 'us'  // Target specific country
});
```

### Antibot Bypass

Bypass Cloudflare, DataDome, PerimeterX and other bot protection:

```typescript
const result = await client.scrape({
  url: 'https://protected-site.com',
  antibot: true,
  premiumProxy: true
});
```

### Screenshots

Capture screenshots of web pages:

```typescript
import fs from 'fs';

// Get base64 screenshot
const screenshot = await client.screenshot('https://example.com');

// Save to file
fs.writeFileSync('screenshot.png', Buffer.from(screenshot, 'base64'));

// Screenshot specific element
const result = await client.scrape({
  url: 'https://example.com',
  jsRender: true,
  screenshotSelector: '.product-card'
});
```

### Domain Extractors

Extract structured data from supported websites:

```typescript
import { AmazonProduct, GoogleSerpResult } from 'clearscrape';

// Amazon product data
const product = await client.extract<AmazonProduct>(
  'https://www.amazon.com/dp/B09V3KXJPB',
  'amazon'
);

console.log(product.title);      // "Apple AirPods Pro..."
console.log(product.price);      // "$249.00"
console.log(product.rating);     // "4.7"
console.log(product.reviewCount); // "125,432"

// Google SERP data
const serp = await client.extract<GoogleSerpResult>(
  'https://www.google.com/search?q=best+laptops',
  'google'
);

console.log(serp.organicResults[0].title);
console.log(serp.featuredSnippet);
console.log(serp.relatedSearches);
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

```typescript
// With Playwright
import { chromium } from 'playwright';

const browser = await chromium.connectOverCDP(
  client.getBrowserWsUrl()
);

const page = await browser.newPage();
await page.goto('https://example.com');

const title = await page.title();
await browser.close();
```

```typescript
// With Puppeteer
import puppeteer from 'puppeteer-core';

const browser = await puppeteer.connect({
  browserWSEndpoint: client.getBrowserWsUrl()
});

const page = await browser.newPage();
await page.goto('https://example.com');

await browser.close();
```

```typescript
// With country targeting
const wsUrl = client.getBrowserWsUrl({ proxyCountry: 'gb' });
```

### Residential Proxies

Use ClearScrape proxies with any HTTP client:

```typescript
// Get proxy configuration
const proxy = client.getProxyConfig();
// { host: 'proxy.clearscrape.io', port: 8000, username: '...', password: '...' }

// Get proxy URL string
const proxyUrl = client.getProxyUrl();
// 'http://apikey:apikey@proxy.clearscrape.io:8000'

// With country targeting
const proxyUrl = client.getProxyUrl({ country: 'us' });

// With session sticky IP
const proxyUrl = client.getProxyUrl({ session: 'my-session-123' });

// Combined
const proxyUrl = client.getProxyUrl({ country: 'us', session: 'abc' });
```

**Use with axios:**
```typescript
import axios from 'axios';
import { HttpsProxyAgent } from 'https-proxy-agent';

const agent = new HttpsProxyAgent(client.getProxyUrl({ country: 'us' }));

const response = await axios.get('https://httpbin.org/ip', {
  httpsAgent: agent
});
```

**Use with node-fetch:**
```typescript
import fetch from 'node-fetch';
import { HttpsProxyAgent } from 'https-proxy-agent';

const agent = new HttpsProxyAgent(client.getProxyUrl());

const response = await fetch('https://httpbin.org/ip', { agent });
```

## Configuration

```typescript
const client = new ClearScrape({
  // Required: Your API key
  apiKey: 'your-api-key',

  // Optional: Custom base URL (default: https://clearscrape.io/api)
  baseUrl: 'https://clearscrape.io/api',

  // Optional: Request timeout in ms (default: 60000)
  timeout: 60000,

  // Optional: Number of retries (default: 3)
  retries: 3
});
```

## Error Handling

```typescript
import {
  ClearScrape,
  ClearScrapeError,
  InsufficientCreditsError,
  RateLimitError
} from 'clearscrape';

try {
  const result = await client.scrape({ url: 'https://example.com' });
} catch (error) {
  if (error instanceof InsufficientCreditsError) {
    console.log(`Need ${error.required} credits`);
  } else if (error instanceof RateLimitError) {
    console.log('Rate limited, try again later');
  } else if (error instanceof ClearScrapeError) {
    console.log(`Error ${error.statusCode}: ${error.message}`);
  }
}
```

## TypeScript

The SDK is written in TypeScript and includes full type definitions:

```typescript
import {
  ClearScrape,
  ScrapeOptions,
  ScrapeResponse,
  AmazonProduct,
  GoogleSerpResult,
  DomainType
} from 'clearscrape';

// Full type safety
const options: ScrapeOptions = {
  url: 'https://example.com',
  jsRender: true,
  premiumProxy: true
};

const result: ScrapeResponse = await client.scrape(options);
```

## API Reference

### `ClearScrape`

Main client class.

#### Constructor

```typescript
new ClearScrape(config: ClearScrapeConfig)
```

#### Methods

| Method | Description |
|--------|-------------|
| `scrape(options)` | Scrape a URL with full options |
| `getHtml(url, options?)` | Get HTML content only |
| `getText(url, options?)` | Get text content only |
| `screenshot(url, options?)` | Capture screenshot |
| `extract(url, domain)` | Extract structured data |
| `getProxyConfig(options?)` | Get proxy configuration object |
| `getProxyUrl(options?)` | Get proxy URL string |
| `getBrowserWsUrl(options?)` | Get Scraping Browser WebSocket URL |

### `ScrapeOptions`

| Option | Type | Description |
|--------|------|-------------|
| `url` | `string` | Target URL (required) |
| `method` | `string` | HTTP method (default: GET) |
| `jsRender` | `boolean` | Enable JS rendering (+5 credits) |
| `premiumProxy` | `boolean` | Use residential proxy (+10 credits) |
| `antibot` | `boolean` | Enable antibot bypass (+25 credits) |
| `proxyCountry` | `string` | 2-letter country code |
| `waitFor` | `string` | CSS selector to wait for |
| `wait` | `number` | Wait time in ms |
| `autoScroll` | `boolean` | Scroll to load content |
| `screenshot` | `boolean` | Capture screenshot |
| `screenshotSelector` | `string` | Screenshot specific element |
| `headers` | `object` | Custom HTTP headers |
| `body` | `string\|object` | Request body |
| `domain` | `DomainType` | Domain extractor |

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
- [GitHub Issues](https://github.com/clearscrape/clearscrape-node/issues)

## License

MIT
