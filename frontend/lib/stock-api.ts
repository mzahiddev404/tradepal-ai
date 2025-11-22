/**
 * Stock market API client
 * Refactored to use Next.js API proxies for robustness
 */

import { apiRequest, ApiError } from "./api-client";
import { API_URL } from "./constants"; // Still used for non-proxied endpoints

export interface StockQuote {
  symbol: string;
  name?: string;
  current_price?: number;
  previous_close?: number;
  change?: number;
  change_percent?: number;
  volume?: number;
  market_cap?: number;
  high_52w?: number;
  low_52w?: number;
  timestamp?: string;
  source?: string;
  error?: string;
}

export interface OptionsChain {
  symbol: string;
  expiration?: string;
  current_price?: number;
  atm_strike?: number;
  strike_range?: number;
  available_expirations?: string[];
  filtered_expirations?: Array<{ date: string; dte: number }>;
  calls?: any[];
  puts?: any[];
  unusual_count?: number;
  timestamp?: string;
  error?: string;
}

export interface MarketOverview {
  indices?: Array<{
    symbol: string;
    name: string;
    price: number;
    change: number;
    change_percent: number;
  }>;
  timestamp?: string;
  error?: string;
}

export interface HistoricalPrice {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface HistoricalPriceRange {
  symbol: string;
  name?: string;
  start_date?: string;
  end_date?: string;
  trading_days?: number;
  prices?: HistoricalPrice[];
  timestamp?: string;
  error?: string;
}

export interface FlowBiasReport {
  symbol: string;
  bias: "BULLISH" | "BEARISH" | "NEUTRAL";
  flow_score: number;
  aggression_ratio: number;
  call_premium: number;
  put_premium: number;
  dominant_expiry: string;
  recommendation: string;
  conviction: string;
}

export interface EventStudyResponse {
  symbol: string;
  flow_report?: FlowBiasReport;
  raw_data_points?: number;
  timestamp?: string;
  error?: string;
  // Legacy fields (kept optional for backward compat if needed, though unused now)
  start_date?: string;
  end_date?: string;
  summary?: any[];
  events?: any[];
}

/**
 * Helper for fetching from local Next.js API routes
 */
async function fetchLocalApi<T>(endpoint: string): Promise<T> {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`Local API error: ${response.statusText}`);
  }
  return await response.json();
}

/**
 * Get stock quote
 * Uses the local proxy /api/stocks for robustness
 */
export async function getStockQuote(symbol: string): Promise<StockQuote> {
  try {
    // Use the robust multi-symbol proxy which handles fallbacks
    const quotes = await fetchLocalApi<StockQuote[]>(`/api/stocks?symbols=${symbol}`);
    if (quotes && quotes.length > 0) {
      return quotes[0];
    }
    throw new Error("No data returned");
  } catch (error) {
    // Fallback to direct backend call if proxy fails (legacy method)
    console.warn("Proxy failed, falling back to direct backend", error);
    return apiRequest<StockQuote>(`/api/stock/quote/${symbol.toUpperCase()}`);
  }
}

/**
 * Get options chain
 * Note: Options data is complex and specific, so we keep using the direct backend route
 * but add better error handling.
 */
export async function getOptionsChain(
  symbol: string,
  expiration?: string,
  filterExpirations: string = "front_week",
  strikeRange: number = 5,
  minPremium: number = 50000,
  showUnusualOnly: boolean = false
): Promise<OptionsChain> {
  const url = new URL(`${API_URL}/api/stock/options/${symbol.toUpperCase()}`);
  if (expiration) {
    url.searchParams.append("expiration", expiration);
  }
  url.searchParams.append("filter_expirations", filterExpirations);
  url.searchParams.append("strike_range", strikeRange.toString());
  url.searchParams.append("min_premium", minPremium.toString());
  url.searchParams.append("show_unusual_only", showUnusualOnly.toString());

  try {
    return await apiRequest<OptionsChain>(url.pathname + url.search);
  } catch (error) {
    if (error instanceof ApiError) {
      throw new ApiError(
        `Failed to fetch options data: ${error.message}`,
        error.status,
        error.statusText
      );
    }
    throw error;
  }
}

/**
 * Get market overview
 * Refactored to use local proxy logic implicitly via stock quotes
 */
export async function getMarketOverview(): Promise<MarketOverview> {
  try {
    // Fetch major indices using our robust proxy
    const indices = ["SPY", "QQQ", "DIA", "IWM"];
    const quotes = await fetchLocalApi<StockQuote[]>(`/api/stocks?symbols=${indices.join(",")}`);
    
    const indicesData = quotes.map(q => ({
      symbol: q.symbol,
      name: q.symbol === "SPY" ? "S&P 500" : 
            q.symbol === "QQQ" ? "NASDAQ 100" : 
            q.symbol === "DIA" ? "Dow Jones" : 
            q.symbol === "IWM" ? "Russell 2000" : q.name || q.symbol,
      price: q.current_price || 0,
      change: q.change || 0,
      change_percent: q.change_percent || 0
    }));

    return {
      indices: indicesData,
      timestamp: new Date().toISOString()
    };
  } catch (error) {
    console.warn("Proxy failed for overview, falling back to direct backend", error);
    return apiRequest<MarketOverview>("/api/stock/market/overview");
  }
}

/**
 * Get multiple stock quotes
 */
export async function getMultipleQuotes(symbols: string[]): Promise<StockQuote[]> {
  const symbolsParam = symbols.map((s) => s.toUpperCase()).join(",");
  try {
    return await fetchLocalApi<StockQuote[]>(`/api/stocks?symbols=${symbolsParam}`);
  } catch (error) {
    return apiRequest<StockQuote[]>(`/api/stock/quotes?symbols=${symbolsParam}`);
  }
}

/**
 * Get historical stock prices for a date range
 */
export async function getHistoricalPriceRange(
  symbol: string,
  days?: number,
  startDate?: string,
  endDate?: string
): Promise<HistoricalPriceRange> {
  const url = new URL(`${API_URL}/api/stock/historical/${symbol.toUpperCase()}/range`);

  if (days !== undefined) {
    url.searchParams.append("days", days.toString());
  }
  if (startDate) {
    url.searchParams.append("start_date", startDate);
  }
  if (endDate) {
    url.searchParams.append("end_date", endDate);
  }

  return apiRequest<HistoricalPriceRange>(url.pathname + url.search);
}

/**
 * Get event study analysis for stock returns around religious holidays
 */
export async function getEventStudy(
  symbol: string,
  startDate?: string,
  endDate?: string,
  windows?: string
): Promise<EventStudyResponse> {
  const url = new URL(`${API_URL}/api/stock/event-study/${symbol.toUpperCase()}`);

  if (startDate) {
    url.searchParams.append("start_date", startDate);
  }
  if (endDate) {
    url.searchParams.append("end_date", endDate);
  }
  if (windows) {
    url.searchParams.append("windows", windows);
  }

  return apiRequest<EventStudyResponse>(url.pathname + url.search);
}
