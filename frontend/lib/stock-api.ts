/**
 * Stock market API client
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
  available_expirations?: string[];
  calls?: any[];
  puts?: any[];
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

/**
 * Get stock quote
 */
export async function getStockQuote(symbol: string): Promise<StockQuote> {
  const response = await fetch(`${API_URL}/api/stock/quote/${symbol.toUpperCase()}`);

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Get options chain
 */
export async function getOptionsChain(
  symbol: string,
  expiration?: string
): Promise<OptionsChain> {
  const url = new URL(`${API_URL}/api/stock/options/${symbol.toUpperCase()}`);
  if (expiration) {
    url.searchParams.append("expiration", expiration);
  }

  const response = await fetch(url.toString());

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Get market overview
 */
export async function getMarketOverview(): Promise<MarketOverview> {
  const response = await fetch(`${API_URL}/api/stock/market/overview`);

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

/**
 * Get multiple stock quotes
 */
export async function getMultipleQuotes(symbols: string[]): Promise<StockQuote[]> {
  const symbolsParam = symbols.map(s => s.toUpperCase()).join(",");
  const response = await fetch(`${API_URL}/api/stock/quotes?symbols=${symbolsParam}`);

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}


