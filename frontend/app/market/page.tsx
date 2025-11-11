"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { StockQuoteDisplay } from "@/components/stock/stock-quote";
import { MarketOverviewDisplay } from "@/components/stock/market-overview";
import {
  getStockQuote,
  getOptionsChain,
  getMarketOverview,
  StockQuote,
  OptionsChain,
  MarketOverview,
} from "@/lib/stock-api";
import { Search, RefreshCw } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

export default function MarketPage() {
  const [marketOverview, setMarketOverview] = useState<MarketOverview | null>(null);
  const [spyQuote, setSpyQuote] = useState<StockQuote | null>(null);
  const [tslaQuote, setTslaQuote] = useState<StockQuote | null>(null);
  const [searchSymbol, setSearchSymbol] = useState("");
  const [searchResult, setSearchResult] = useState<StockQuote | null>(null);
  const [optionsData, setOptionsData] = useState<OptionsChain | null>(null);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadMarketData();
  }, []);

  const loadMarketData = async () => {
    setLoading(true);
    try {
      const [overview, spy, tsla] = await Promise.all([
        getMarketOverview(),
        getStockQuote("SPY"),
        getStockQuote("TSLA"),
      ]);
      setMarketOverview(overview);
      setSpyQuote(spy);
      setTslaQuote(tsla);
    } catch (error) {
      console.error("Error loading market data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchSymbol.trim()) return;

    setLoading(true);
    try {
      const quote = await getStockQuote(searchSymbol.trim());
      setSearchResult(quote);
      setSelectedSymbol(quote.symbol);
      
      // Load options for the searched symbol
      try {
        const options = await getOptionsChain(quote.symbol);
        setOptionsData(options);
      } catch (error) {
        console.error("Error loading options:", error);
      }
    } catch (error) {
      console.error("Error searching:", error);
      setSearchResult({
        symbol: searchSymbol.trim(),
        error: "Failed to fetch stock data",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadOptions = async (symbol: string) => {
    setLoading(true);
    try {
      const options = await getOptionsChain(symbol);
      setOptionsData(options);
      setSelectedSymbol(symbol);
    } catch (error) {
      console.error("Error loading options:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Market Data</h1>
          <p className="text-muted-foreground">
            Real-time stock quotes and options data (Demo Application)
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadMarketData} disabled={loading}>
            <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin")} />
            Refresh
          </Button>
          <Link href="/disclaimer">
            <Button variant="outline">Disclaimer</Button>
          </Link>
          <Link href="/">
            <Button variant="outline">Chat</Button>
          </Link>
        </div>
      </div>

      {/* Market Overview */}
      {marketOverview && <MarketOverviewDisplay overview={marketOverview} />}

      {/* Search */}
      <Card className="p-4">
        <div className="flex gap-2">
          <Input
            placeholder="Search stock symbol (e.g., AAPL, MSFT)"
            value={searchSymbol}
            onChange={(e) => setSearchSymbol(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <Button onClick={handleSearch} disabled={loading}>
            <Search className="h-4 w-4 mr-2" />
            Search
          </Button>
        </div>
      </Card>

      {/* SPY and TSLA Quotes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {spyQuote && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-lg font-semibold">SPY (S&P 500)</h2>
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadOptions("SPY")}
              >
                View Options
              </Button>
            </div>
            <StockQuoteDisplay quote={spyQuote} />
          </div>
        )}
        {tslaQuote && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-lg font-semibold">TSLA (Tesla)</h2>
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadOptions("TSLA")}
              >
                View Options
              </Button>
            </div>
            <StockQuoteDisplay quote={tslaQuote} />
          </div>
        )}
      </div>

      {/* Search Result */}
      {searchResult && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-semibold">
              {searchResult.symbol}
              {searchResult.name && ` - ${searchResult.name}`}
            </h2>
            {!searchResult.error && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadOptions(searchResult.symbol)}
              >
                View Options
              </Button>
            )}
          </div>
          <StockQuoteDisplay quote={searchResult} />
        </div>
      )}

      {/* Options Chain */}
      {optionsData && selectedSymbol && !optionsData.error && (
        <Card className="p-4">
          <h2 className="text-lg font-semibold mb-4">
            Options Chain: {selectedSymbol} - {optionsData.expiration}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {optionsData.calls && optionsData.calls.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">Calls</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {optionsData.calls.map((call: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-2 border rounded text-sm grid grid-cols-4 gap-2"
                    >
                      <div>
                        <p className="text-xs text-muted-foreground">Strike</p>
                        <p className="font-semibold">${call.strike?.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Last</p>
                        <p>${call.lastPrice?.toFixed(2) || "N/A"}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Bid</p>
                        <p>${call.bid?.toFixed(2) || "N/A"}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Ask</p>
                        <p>${call.ask?.toFixed(2) || "N/A"}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {optionsData.puts && optionsData.puts.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">Puts</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {optionsData.puts.map((put: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-2 border rounded text-sm grid grid-cols-4 gap-2"
                    >
                      <div>
                        <p className="text-xs text-muted-foreground">Strike</p>
                        <p className="font-semibold">${put.strike?.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Last</p>
                        <p>${put.lastPrice?.toFixed(2) || "N/A"}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Bid</p>
                        <p>${put.bid?.toFixed(2) || "N/A"}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Ask</p>
                        <p>${put.ask?.toFixed(2) || "N/A"}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}

