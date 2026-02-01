/**
 * ClearScrape Node.js SDK
 *
 * Official Node.js client for the ClearScrape web scraping API.
 *
 * @packageDocumentation
 *
 * @example
 * Basic usage:
 * ```typescript
 * import { ClearScrape } from 'clearscrape';
 *
 * const client = new ClearScrape({
 *   apiKey: process.env.CLEARSCRAPE_API_KEY
 * });
 *
 * // Simple scrape
 * const result = await client.scrape({
 *   url: 'https://example.com'
 * });
 * console.log(result.data.html);
 *
 * // With JavaScript rendering
 * const result = await client.scrape({
 *   url: 'https://example.com',
 *   jsRender: true,
 *   waitFor: '.content'
 * });
 *
 * // Extract structured data from Amazon
 * const product = await client.extract(
 *   'https://www.amazon.com/dp/B09V3KXJPB',
 *   'amazon'
 * );
 * console.log(product.title, product.price);
 * ```
 */

// Export main client
export { ClearScrape } from './client';

// Export all types
export type {
  ClearScrapeConfig,
  ScrapeOptions,
  ScrapeResponse,
  ScrapeErrorResponse,
  DomainType,
  AmazonProduct,
  GoogleSerpResult,
  ProxyConfig,
  BrowserOptions,
} from './types';

// Export error classes
export {
  ClearScrapeError,
  InsufficientCreditsError,
  RateLimitError,
} from './types';

// Default export for convenience
export { ClearScrape as default } from './client';
