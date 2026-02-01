/**
 * ClearScrape SDK Types
 */

/**
 * Configuration options for the ClearScrape client
 */
export interface ClearScrapeConfig {
  /** Your ClearScrape API key */
  apiKey: string;
  /** Base URL for the API (defaults to https://api.clearscrape.io) */
  baseUrl?: string;
  /** Request timeout in milliseconds (defaults to 60000) */
  timeout?: number;
  /** Number of retries for failed requests (defaults to 3) */
  retries?: number;
}

/**
 * Options for scraping a URL
 */
export interface ScrapeOptions {
  /** Target URL to scrape */
  url: string;
  /** HTTP method (defaults to GET) */
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  /** Enable JavaScript rendering (+5 credits) */
  jsRender?: boolean;
  /** Use premium residential proxies (+10 credits) */
  premiumProxy?: boolean;
  /** Enable antibot bypass (+25 credits) */
  antibot?: boolean;
  /** 2-letter country code for geo-targeting */
  proxyCountry?: string;
  /** CSS selector to wait for (requires jsRender) */
  waitFor?: string;
  /** Fixed wait time in milliseconds (max 30000) */
  wait?: number;
  /** Scroll page to load lazy content */
  autoScroll?: boolean;
  /** Capture full page screenshot */
  screenshot?: boolean;
  /** Capture screenshot of specific element */
  screenshotSelector?: string;
  /** Custom HTTP headers */
  headers?: Record<string, string>;
  /** Request body for POST/PUT requests */
  body?: string | Record<string, unknown>;
  /** Domain extractor (amazon, walmart, google, etc.) */
  domain?: DomainType;
}

/**
 * Supported domain extractors
 */
export type DomainType =
  | 'amazon'
  | 'walmart'
  | 'google'
  | 'google_shopping'
  | 'ebay'
  | 'target'
  | 'etsy'
  | 'bestbuy'
  | 'homedepot'
  | 'zillow'
  | 'yelp'
  | 'indeed'
  | 'linkedin_jobs';

/**
 * Response from a successful scrape request
 */
export interface ScrapeResponse {
  success: true;
  data: {
    /** Raw HTML content */
    html: string;
    /** Extracted text content */
    text?: string;
    /** Base64 encoded screenshot (if requested) */
    screenshot?: string;
    /** Extracted data (if domain extractor used) */
    extracted?: Record<string, unknown>;
  };
  metadata: {
    /** Final URL after redirects */
    url: string;
    /** HTTP status code */
    statusCode: number;
    /** Credits consumed */
    cost: number;
    /** Request duration in milliseconds */
    duration: number;
    /** Response size in bytes */
    byteSize: number;
    /** Options used for the request */
    options: {
      js_render: boolean;
      premium_proxy: boolean;
      antibot: boolean;
      proxy_country?: string;
    };
    /** Domain extractor used */
    domain?: string;
  };
}

/**
 * Response from a failed scrape request
 */
export interface ScrapeErrorResponse {
  success: false;
  error: string;
  message: string;
  /** Credits required (for insufficient credits error) */
  required?: number;
}

/**
 * Amazon product data extracted by domain API
 */
export interface AmazonProduct {
  title: string;
  price: string;
  originalPrice?: string;
  currency: string;
  rating: string;
  reviewCount: string;
  availability: string;
  seller: string;
  asin: string;
  brand?: string;
  images: string[];
  features: string[];
  breadcrumbs: string[];
  description?: string;
  specifications?: Record<string, string>;
}

/**
 * Google SERP data extracted by domain API
 */
export interface GoogleSerpResult {
  searchQuery: string;
  totalResults: string;
  organicResults: Array<{
    position: number;
    title: string;
    url: string;
    displayUrl: string;
    description: string;
  }>;
  featuredSnippet?: {
    title: string;
    content: string;
    url: string;
  };
  peopleAlsoAsk?: Array<{
    question: string;
    answer: string;
  }>;
  relatedSearches?: string[];
}

/**
 * Proxy configuration for residential proxy service
 */
export interface ProxyConfig {
  host: string;
  port: number;
  username: string;
  password: string;
}

/**
 * Browser connection options for Scraping Browser
 */
export interface BrowserOptions {
  /** 2-letter country code for geo-targeting */
  proxyCountry?: string;
}

/**
 * ClearScrape API error
 */
export class ClearScrapeError extends Error {
  public readonly statusCode: number;
  public readonly response?: ScrapeErrorResponse;

  constructor(message: string, statusCode: number, response?: ScrapeErrorResponse) {
    super(message);
    this.name = 'ClearScrapeError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

/**
 * Insufficient credits error
 */
export class InsufficientCreditsError extends ClearScrapeError {
  public readonly required: number;

  constructor(message: string, required: number) {
    super(message, 402);
    this.name = 'InsufficientCreditsError';
    this.required = required;
  }
}

/**
 * Rate limit error
 */
export class RateLimitError extends ClearScrapeError {
  constructor(message: string) {
    super(message, 429);
    this.name = 'RateLimitError';
  }
}
