import {
  ClearScrapeConfig,
  ScrapeOptions,
  ScrapeResponse,
  ScrapeErrorResponse,
  ProxyConfig,
  BrowserOptions,
  ClearScrapeError,
  InsufficientCreditsError,
  RateLimitError,
} from './types';

const DEFAULT_BASE_URL = 'https://api.clearscrape.io';
const DEFAULT_TIMEOUT = 60000;
const DEFAULT_RETRIES = 3;

/**
 * ClearScrape API Client
 *
 * @example
 * ```typescript
 * import { ClearScrape } from 'clearscrape';
 *
 * const client = new ClearScrape({ apiKey: 'your-api-key' });
 *
 * const result = await client.scrape({
 *   url: 'https://example.com',
 *   jsRender: true
 * });
 *
 * console.log(result.data.html);
 * ```
 */
export class ClearScrape {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly timeout: number;
  private readonly retries: number;

  constructor(config: ClearScrapeConfig) {
    if (!config.apiKey) {
      throw new Error('API key is required');
    }

    this.apiKey = config.apiKey;
    this.baseUrl = config.baseUrl || DEFAULT_BASE_URL;
    this.timeout = config.timeout || DEFAULT_TIMEOUT;
    this.retries = config.retries ?? DEFAULT_RETRIES;
  }

  /**
   * Scrape a URL and return the HTML content
   *
   * @param options - Scraping options
   * @returns Promise resolving to scrape response
   *
   * @example
   * ```typescript
   * // Basic scrape
   * const result = await client.scrape({ url: 'https://example.com' });
   *
   * // With JavaScript rendering
   * const result = await client.scrape({
   *   url: 'https://example.com',
   *   jsRender: true,
   *   waitFor: '.content'
   * });
   *
   * // With premium proxy and country targeting
   * const result = await client.scrape({
   *   url: 'https://example.com',
   *   premiumProxy: true,
   *   proxyCountry: 'us'
   * });
   * ```
   */
  async scrape(options: ScrapeOptions): Promise<ScrapeResponse> {
    const payload = this.buildPayload(options);
    return this.makeRequest('/api/scrape', payload);
  }

  /**
   * Scrape a URL and return only the HTML content
   *
   * @param url - URL to scrape
   * @param options - Additional scraping options
   * @returns Promise resolving to HTML string
   */
  async getHtml(url: string, options?: Omit<ScrapeOptions, 'url'>): Promise<string> {
    const result = await this.scrape({ url, ...options });
    return result.data.html;
  }

  /**
   * Scrape a URL and return only the text content
   *
   * @param url - URL to scrape
   * @param options - Additional scraping options
   * @returns Promise resolving to text string
   */
  async getText(url: string, options?: Omit<ScrapeOptions, 'url'>): Promise<string> {
    const result = await this.scrape({ url, ...options });
    return result.data.text || '';
  }

  /**
   * Take a screenshot of a URL
   *
   * @param url - URL to screenshot
   * @param options - Additional options
   * @returns Promise resolving to base64 encoded screenshot
   *
   * @example
   * ```typescript
   * const screenshot = await client.screenshot('https://example.com');
   * // Save to file
   * fs.writeFileSync('screenshot.png', Buffer.from(screenshot, 'base64'));
   * ```
   */
  async screenshot(
    url: string,
    options?: Omit<ScrapeOptions, 'url' | 'screenshot'>
  ): Promise<string> {
    const result = await this.scrape({
      url,
      ...options,
      jsRender: true,
      screenshot: true,
    });

    if (!result.data.screenshot) {
      throw new ClearScrapeError('Screenshot not returned', 500);
    }

    // Remove data URL prefix if present
    const base64 = result.data.screenshot.replace(/^data:image\/\w+;base64,/, '');
    return base64;
  }

  /**
   * Scrape using a domain-specific extractor (Amazon, Walmart, Google, etc.)
   *
   * @param url - URL to scrape
   * @param domain - Domain extractor to use
   * @returns Promise resolving to extracted data
   *
   * @example
   * ```typescript
   * // Extract Amazon product data
   * const product = await client.extract(
   *   'https://www.amazon.com/dp/B09V3KXJPB',
   *   'amazon'
   * );
   * console.log(product.title, product.price);
   *
   * // Extract Google SERP data
   * const serp = await client.extract(
   *   'https://www.google.com/search?q=best+laptops',
   *   'google'
   * );
   * console.log(serp.organicResults);
   * ```
   */
  async extract<T = Record<string, unknown>>(
    url: string,
    domain: ScrapeOptions['domain']
  ): Promise<T> {
    const result = await this.scrape({ url, domain });

    if (!result.data.extracted) {
      throw new ClearScrapeError('No extracted data returned', 500);
    }

    return result.data.extracted as T;
  }

  /**
   * Get proxy configuration for the residential proxy service
   *
   * @param options - Proxy options
   * @returns Proxy configuration object
   *
   * @example
   * ```typescript
   * // Basic proxy config
   * const proxy = client.getProxyConfig();
   * // { host: 'proxy.clearscrape.io', port: 8000, username: '...', password: '...' }
   *
   * // With country targeting
   * const proxy = client.getProxyConfig({ country: 'us' });
   *
   * // With session sticky IP
   * const proxy = client.getProxyConfig({ session: 'my-session-123' });
   * ```
   */
  getProxyConfig(options?: { country?: string; session?: string }): ProxyConfig {
    let username = this.apiKey;

    if (options?.country) {
      username += `-country-${options.country}`;
    }

    if (options?.session) {
      username += `-session-${options.session}`;
    }

    return {
      host: 'proxy.clearscrape.io',
      port: 8000,
      username,
      password: this.apiKey,
    };
  }

  /**
   * Get proxy URL string for use with HTTP clients
   *
   * @param options - Proxy options
   * @returns Proxy URL string
   *
   * @example
   * ```typescript
   * const proxyUrl = client.getProxyUrl({ country: 'us' });
   * // 'http://apikey-country-us:apikey@proxy.clearscrape.io:8000'
   *
   * // Use with axios
   * const HttpsProxyAgent = require('https-proxy-agent');
   * const agent = new HttpsProxyAgent(client.getProxyUrl());
   * axios.get(url, { httpsAgent: agent });
   * ```
   */
  getProxyUrl(options?: { country?: string; session?: string }): string {
    const config = this.getProxyConfig(options);
    return `http://${config.username}:${config.password}@${config.host}:${config.port}`;
  }

  /**
   * Get WebSocket URL for Scraping Browser (Playwright/Puppeteer)
   *
   * @param options - Browser options
   * @returns WebSocket URL string
   *
   * @example
   * ```typescript
   * // Use with Playwright
   * const { chromium } = require('playwright');
   * const browser = await chromium.connectOverCDP(client.getBrowserWsUrl());
   *
   * // Use with Puppeteer
   * const puppeteer = require('puppeteer-core');
   * const browser = await puppeteer.connect({
   *   browserWSEndpoint: client.getBrowserWsUrl()
   * });
   *
   * // With country targeting
   * const wsUrl = client.getBrowserWsUrl({ proxyCountry: 'gb' });
   * ```
   */
  getBrowserWsUrl(options?: BrowserOptions): string {
    let url = `wss://browser.clearscrape.io?apiKey=${this.apiKey}`;

    if (options?.proxyCountry) {
      url += `&proxy_country=${options.proxyCountry}`;
    }

    return url;
  }

  /**
   * Build the API request payload
   */
  private buildPayload(options: ScrapeOptions): Record<string, unknown> {
    const payload: Record<string, unknown> = {
      url: options.url,
    };

    if (options.method) payload.method = options.method;
    if (options.jsRender) payload.js_render = options.jsRender;
    if (options.premiumProxy) payload.premium_proxy = options.premiumProxy;
    if (options.antibot) payload.antibot = options.antibot;
    if (options.proxyCountry) payload.proxy_country = options.proxyCountry;
    if (options.waitFor) payload.wait_for = options.waitFor;
    if (options.wait) payload.wait = options.wait;
    if (options.autoScroll) payload.auto_scroll = options.autoScroll;
    if (options.screenshot) payload.screenshot = options.screenshot;
    if (options.screenshotSelector) payload.screenshot_selector = options.screenshotSelector;
    if (options.headers) payload.headers = options.headers;
    if (options.body) payload.body = options.body;
    if (options.domain) payload.domain = options.domain;

    return payload;
  }

  /**
   * Make an API request with retries
   */
  private async makeRequest(
    endpoint: string,
    payload: Record<string, unknown>,
    attempt: number = 1
  ): Promise<ScrapeResponse> {
    const url = `${this.baseUrl}${endpoint}`;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'X-API-Key': this.apiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const data = await response.json();

      if (!response.ok) {
        return this.handleError(response.status, data as ScrapeErrorResponse, payload, attempt);
      }

      return data as ScrapeResponse;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error && error.name === 'AbortError') {
        throw new ClearScrapeError('Request timeout', 408);
      }

      // Retry on network errors
      if (attempt < this.retries) {
        const delay = Math.pow(2, attempt) * 1000;
        await this.sleep(delay);
        return this.makeRequest(endpoint, payload, attempt + 1);
      }

      throw new ClearScrapeError(
        error instanceof Error ? error.message : 'Unknown error',
        500
      );
    }
  }

  /**
   * Handle API errors
   */
  private async handleError(
    statusCode: number,
    response: ScrapeErrorResponse,
    payload: Record<string, unknown>,
    attempt: number
  ): Promise<ScrapeResponse> {
    // Don't retry client errors (except rate limits)
    if (statusCode >= 400 && statusCode < 500 && statusCode !== 429) {
      if (statusCode === 402 && response.required) {
        throw new InsufficientCreditsError(response.message, response.required);
      }
      throw new ClearScrapeError(response.message || response.error, statusCode, response);
    }

    // Retry rate limits and server errors
    if (attempt < this.retries) {
      const delay = statusCode === 429 ? 5000 : Math.pow(2, attempt) * 1000;
      await this.sleep(delay);
      return this.makeRequest('/api/scrape', payload, attempt + 1);
    }

    if (statusCode === 429) {
      throw new RateLimitError(response.message || 'Rate limit exceeded');
    }

    throw new ClearScrapeError(response.message || response.error, statusCode, response);
  }

  /**
   * Sleep for a specified duration
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
