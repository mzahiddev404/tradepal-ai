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
  expiration?: string,
  filterExpirations: string = "front_week",
  strikeRange: number = 5,
  minPremium: number = 50000,
  showUnusualOnly: boolean = false
): Promise<OptionsChain> {
  try {
    const url = new URL(`${API_URL}/api/stock/options/${symbol.toUpperCase()}`);
    if (expiration) {
      url.searchParams.append("expiration", expiration);
    }
    url.searchParams.append("filter_expirations", filterExpirations);
    url.searchParams.append("strike_range", strikeRange.toString());
    url.searchParams.append("min_premium", minPremium.toString());
    url.searchParams.append("show_unusual_only", showUnusualOnly.toString());

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Options API error (${response.status}):`, errorText);
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching options chain:', error);
    throw error;
  }
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

/**
 * Get historical stock prices for a date range
 */
export async function getHistoricalPriceRange(
  symbol: string,
  days?: number,
  startDate?: string,
  endDate?: string
): Promise<HistoricalPriceRange> {
  try {
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

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Historical range API error (${response.status}):`, errorText);
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching historical price range:', error);
    throw error;
  }
}


