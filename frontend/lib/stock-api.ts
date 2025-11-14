/**
 * Stock market API client
 * Refactored with better error handling
 */

import { apiRequest, ApiError } from "./api-client";
import { API_URL } from "./constants";

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

export interface EventStudySummary {
  holiday: string;
  window: string;
  count: number;
  mean: number;
  std: number;
  t_stat: number;
  bootstrap_p: number;
  n: number;
}

export interface EventStudyEvent {
  holiday: string;
  event_date: string;
  window: string;
  cum_return: number;
}

export interface EventStudyResponse {
  symbol: string;
  start_date?: string;
  end_date?: string;
  summary?: EventStudySummary[];
  events?: EventStudyEvent[];
  research_insights?: Record<string, any>;
  general_findings?: string[];
  disclaimers?: string[];
  timestamp?: string;
  error?: string;
}

/**
 * Get stock quote
 */
export async function getStockQuote(symbol: string): Promise<StockQuote> {
  return apiRequest<StockQuote>(`/api/stock/quote/${symbol.toUpperCase()}`);
}

/**
 * Get options chain
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
    // Provide more context for options-specific errors
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
 */
export async function getMarketOverview(): Promise<MarketOverview> {
  return apiRequest<MarketOverview>("/api/stock/market/overview");
}

/**
 * Get multiple stock quotes
 */
export async function getMultipleQuotes(symbols: string[]): Promise<StockQuote[]> {
  const symbolsParam = symbols.map((s) => s.toUpperCase()).join(",");
  return apiRequest<StockQuote[]>(`/api/stock/quotes?symbols=${symbolsParam}`);
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


