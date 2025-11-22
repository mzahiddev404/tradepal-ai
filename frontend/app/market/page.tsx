"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { StockQuoteDisplay } from "@/components/stock/stock-quote";
import { MarketOverviewDisplay } from "@/components/stock/market-overview";
import { EventStudy } from "@/components/stock/event-study";
import {
  getStockQuote,
  getOptionsChain,
  getMarketOverview,
  StockQuote,
  OptionsChain,
  MarketOverview,
} from "@/lib/stock-api";
import { Search, RefreshCw, AlertCircle } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { MarketTime } from "@/components/chat/market-time";
import { useRouter } from "next/navigation";

export default function MarketPage() {
  const router = useRouter();
  const [marketOverview, setMarketOverview] = useState<MarketOverview | null>(null);
  const [spyQuote, setSpyQuote] = useState<StockQuote | null>(null);
  const [tslaQuote, setTslaQuote] = useState<StockQuote | null>(null);
  const [searchSymbol, setSearchSymbol] = useState("");
  const [searchResult, setSearchResult] = useState<StockQuote | null>(null);
  const [optionsData, setOptionsData] = useState<OptionsChain | null>(null);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  // Filter states
  const [selectedExpiration, setSelectedExpiration] = useState<string>("");
  const [strikeRange, setStrikeRange] = useState<number[]>([5]);
  const [minPremium, setMinPremium] = useState<number>(50000);
  const [showUnusualOnly, setShowUnusualOnly] = useState<boolean>(false);
  const [filterExpirations, setFilterExpirations] = useState<string>("front_week");

  useEffect(() => {
    loadMarketData();
  }, []);

  useEffect(() => {
    if (optionsData && optionsData.filtered_expirations) {
      // Auto-select earliest expiration
      if (!selectedExpiration && optionsData.filtered_expirations.length > 0) {
        setSelectedExpiration(optionsData.filtered_expirations[0].date);
      }
    }
  }, [optionsData]);

  const loadMarketData = async () => {
    setLoading(true);
    try {
      // Use individual error handling so one failure doesn't break the whole page
      const [overview, spy, tsla] = await Promise.all([
        getMarketOverview().catch(e => { console.warn("Overview failed", e); return null; }),
        getStockQuote("SPY").catch(e => { console.warn("SPY failed", e); return null; }),
        getStockQuote("TSLA").catch(e => { console.warn("TSLA failed", e); return null; }),
      ]);
      
      if (overview) setMarketOverview(overview);
      if (spy) setSpyQuote(spy);
      if (tsla) {
        setTslaQuote(tsla);
        // Auto-select TSLA on load so Event Study appears immediately
        if (!selectedSymbol) setSelectedSymbol(tsla.symbol);
      }
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
      await loadOptionsWithFilters(quote.symbol);
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

  const loadOptionsWithFilters = async (symbol: string, expiration?: string) => {
    setLoading(true);
    try {
      const options = await getOptionsChain(
        symbol,
        expiration || selectedExpiration || undefined,
        filterExpirations,
        strikeRange[0],
        minPremium,
        showUnusualOnly
      );
      
      // Check for error response
      if (options.error) {
        console.warn("Options data unavailable:", options.error);
        setOptionsData({
            symbol: symbol,
            error: options.error
        });
        return;
      }

      setOptionsData(options);
      setSelectedSymbol(symbol);
      if (options.filtered_expirations && options.filtered_expirations.length > 0 && !expiration) {
        setSelectedExpiration(options.filtered_expirations[0].date);
      }
    } catch (error) {
      console.warn("Failed to fetch options (likely market closed or rate limit):", error);
      // Set a "graceful" error state that doesn't break the UI
      setOptionsData({
        symbol: symbol,
        error: "Options data temporarily unavailable"
      });
    } finally {
      setLoading(false);
    }
  };

  const loadOptions = async (symbol: string) => {
    await loadOptionsWithFilters(symbol);
  };

  const handleExpirationChange = (expiration: string) => {
    setSelectedExpiration(expiration);
    if (selectedSymbol) {
      loadOptionsWithFilters(selectedSymbol, expiration);
    }
  };

  const handleFilterChange = async () => {
    if (selectedSymbol) {
      await loadOptionsWithFilters(selectedSymbol);
    }
  };

  const formatExpiration = (date: string, dte: number) => {
    const expDate = new Date(date);
    const month = expDate.toLocaleString('default', { month: 'short' });
    const day = expDate.getDate();
    return `${month} ${day}, ${expDate.getFullYear()} (${dte}DTE)`;
  };

  const formatPremium = (premium: number) => {
    if (premium >= 1000000) return `$${(premium / 1000000).toFixed(1)}M`;
    if (premium >= 1000) return `$${(premium / 1000).toFixed(0)}K`;
    return `$${premium.toFixed(0)}`;
  };

  const getFlowPatternColor = (pattern: string) => {
    switch (pattern) {
      case "program":
        return "bg-blue-500";
      case "spread":
        return "bg-purple-500";
      default:
        return "bg-gray-500";
    }
  };

  const getUnusualActivityColor = (premium: number, ratio: number) => {
    if (premium >= 100000 || ratio > 3.0) return "bg-red-500";
    if (premium >= 50000 || ratio > 2.0) return "bg-green-500";
    return "bg-yellow-500";
  };

  return (
    <div className="flex h-screen w-full bg-[#0F1115] bg-grid-subtle text-[#dcdcdc] overflow-hidden">
      {/* Sidebar */}
      <AppSidebar 
        chatMode="standard" 
        onModeChange={() => router.push("/")}
        showDocuments={false}
        onToggleDocuments={() => router.push("/")}
      />

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="h-14 border-b border-white/5 flex items-center justify-between px-4 sm:px-6 bg-[#131619]/50 backdrop-blur-sm shrink-0 z-10">
           <div className="flex items-center gap-3 md:hidden">
             <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-gradient-to-br from-[#34c759] to-[#28a745]">
               <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
               </svg>
             </div>
             <span className="font-bold text-white tracking-tight">TRADEPAL</span>
          </div>

          <div className="hidden md:flex items-center text-sm font-medium text-gray-400">
             <span className="text-gray-500">Workspace</span>
             <span className="mx-2">/</span>
             <span className="text-white">Live Markets</span>
          </div>

          <div className="flex items-center gap-4">
            <MarketTime />
          </div>
        </header>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-6 custom-scrollbar">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-semibold text-[#dcdcdc] uppercase tracking-tight">Market Data</h1>
              <p className="text-sm text-[#969696] mt-1 uppercase tracking-wide">
                Real-time stock quotes and options data
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button 
                variant="outline" 
                onClick={loadMarketData} 
                disabled={loading}
                className="h-9 btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a]"
              >
                <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin")} />
                Refresh
              </Button>
            </div>
          </div>

          {/* Market Overview */}
          {marketOverview && <MarketOverviewDisplay overview={marketOverview} />}

          {/* Search */}
          <Card className="trading-panel p-4 border border-[#2d3237]">
            <div className="flex gap-2">
              <Input
                placeholder="Search stock symbol (e.g., AAPL, MSFT)"
                value={searchSymbol}
                onChange={(e) => setSearchSymbol(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="border-[#2d3237] focus:border-[#007aff] focus:ring-[#007aff]/20 bg-[#23272c] text-[#dcdcdc] placeholder:text-[#6a6a6a]"
              />
              <Button 
                onClick={handleSearch} 
                disabled={loading}
                className="btn-trading-primary"
              >
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
                  <h2 className="text-lg font-semibold text-[#dcdcdc] uppercase tracking-wide">SPY (S&P 500)</h2>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => loadOptions("SPY")}
                    className="btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a]"
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
                  <h2 className="text-lg font-semibold text-[#dcdcdc] uppercase tracking-wide">TSLA (Tesla)</h2>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => loadOptions("TSLA")}
                    className="btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a]"
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
                <h2 className="text-lg font-semibold text-[#dcdcdc] uppercase tracking-wide">
                  {searchResult.symbol}
                  {searchResult.name && ` - ${searchResult.name}`}
                </h2>
                {!searchResult.error && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => loadOptions(searchResult.symbol)}
                    className="btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a]"
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
            <Card className="trading-panel p-4 sm:p-6 border border-[#2d3237]">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-[#dcdcdc] uppercase tracking-wide">
                    Options Chain: {selectedSymbol}
                  </h2>
                  {optionsData.current_price && optionsData.atm_strike && (
                    <p className="text-sm text-[#969696] mt-1 trading-number">
                      Current: ${optionsData.current_price.toFixed(2)} | ATM: ${optionsData.atm_strike.toFixed(2)} | 
                      Showing {optionsData.unusual_count || 0} unusual options
                    </p>
                  )}
                </div>
              </div>

              {/* Filters */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4 p-4 bg-[#23272c] rounded border border-[#2d3237]">
                <div className="space-y-2">
                  <Label>Expiration</Label>
                  <Select
                    value={selectedExpiration}
                    onValueChange={handleExpirationChange}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select expiration" />
                    </SelectTrigger>
                    <SelectContent>
                      {optionsData.filtered_expirations?.map((exp) => (
                        <SelectItem key={exp.date} value={exp.date}>
                          {formatExpiration(exp.date, exp.dte)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Strike Range: ATM ±{strikeRange[0]}</Label>
                  <Slider
                    value={strikeRange}
                    onValueChange={async (value) => {
                      setStrikeRange(value);
                      await handleFilterChange();
                    }}
                    min={3}
                    max={10}
                    step={1}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Min Premium: ${(minPremium / 1000).toFixed(0)}K</Label>
                  <Input
                    type="number"
                    value={minPremium}
                    onChange={async (e) => {
                      setMinPremium(Number(e.target.value));
                      // Debounce: only call after user stops typing
                      setTimeout(() => handleFilterChange(), 500);
                    }}
                    min={0}
                    step={10000}
                  />
                </div>

                <div className="flex items-center space-x-2 pt-6">
                  <Switch
                    checked={showUnusualOnly}
                    onCheckedChange={async (checked) => {
                      setShowUnusualOnly(checked);
                      await handleFilterChange();
                    }}
                  />
                  <Label>Show unusual only</Label>
                </div>
              </div>

              {/* Options Tables */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {optionsData.calls && optionsData.calls.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-2 flex items-center gap-2">
                      Calls
                      {optionsData.expiration && (
                        <span className="text-sm text-muted-foreground">
                          ({optionsData.expiration})
                        </span>
                      )}
                    </h3>
                    <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
                      {optionsData.calls.map((call: any, idx: number) => (
                        <div
                          key={idx}
                          className={cn(
                            "p-2 border rounded text-sm",
                            call.is_atm && "border-2 border-blue-500 bg-blue-50 dark:bg-blue-950",
                            call.unusual_activity && "bg-yellow-50 dark:bg-yellow-950"
                          )}
                        >
                          <div className="grid grid-cols-5 gap-2 items-center">
                            <div>
                              <p className="text-xs text-muted-foreground">Strike</p>
                              <p className="font-semibold flex items-center gap-1">
                                ${call.strike?.toFixed(2)}
                                {call.is_atm && (
                                  <Badge variant="outline" className="text-xs">ATM</Badge>
                                )}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Last</p>
                              <p>${call.lastPrice?.toFixed(2) || "N/A"}</p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Vol/OI</p>
                              <p className="text-xs">
                                {call.volume_to_oi_ratio?.toFixed(2) || "N/A"}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Premium</p>
                              <p className="text-xs font-semibold">
                                {call.estimated_premium ? formatPremium(call.estimated_premium) : "N/A"}
                              </p>
                            </div>
                            <div className="flex flex-col gap-1">
                              {call.unusual_activity && (
                                <TooltipProvider>
                                  <Tooltip>
                                    <TooltipTrigger>
                                      <Badge
                                        className={cn(
                                          "text-xs",
                                          getUnusualActivityColor(
                                            call.estimated_premium || 0,
                                            call.volume_to_oi_ratio || 0
                                          )
                                        )}
                                      >
                                        <AlertCircle className="h-3 w-3 mr-1" />
                                        Unusual
                                      </Badge>
                                    </TooltipTrigger>
                                    <TooltipContent>
                                      <p className="text-xs">{call.activity_reason}</p>
                                    </TooltipContent>
                                  </Tooltip>
                                </TooltipProvider>
                              )}
                              {call.flow_pattern && call.flow_pattern !== "isolated" && (
                                <Badge
                                  variant="outline"
                                  className={cn("text-xs", getFlowPatternColor(call.flow_pattern))}
                                >
                                  {call.flow_pattern}
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {optionsData.puts && optionsData.puts.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-2 flex items-center gap-2">
                      Puts
                      {optionsData.expiration && (
                        <span className="text-sm text-muted-foreground">
                          ({optionsData.expiration})
                        </span>
                      )}
                    </h3>
                    <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
                      {optionsData.puts.map((put: any, idx: number) => (
                        <div
                          key={idx}
                          className={cn(
                            "p-2 border rounded text-sm",
                            put.is_atm && "border-2 border-blue-500 bg-blue-50 dark:bg-blue-950",
                            put.unusual_activity && "bg-yellow-50 dark:bg-yellow-950"
                          )}
                        >
                          <div className="grid grid-cols-5 gap-2 items-center">
                            <div>
                              <p className="text-xs text-muted-foreground">Strike</p>
                              <p className="font-semibold flex items-center gap-1">
                                ${put.strike?.toFixed(2)}
                                {put.is_atm && (
                                  <Badge variant="outline" className="text-xs">ATM</Badge>
                                )}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Last</p>
                              <p>${put.lastPrice?.toFixed(2) || "N/A"}</p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Vol/OI</p>
                              <p className="text-xs">
                                {put.volume_to_oi_ratio?.toFixed(2) || "N/A"}
                              </p>
                            </div>
                            <div>
                              <p className="text-xs text-muted-foreground">Premium</p>
                              <p className="text-xs font-semibold">
                                {put.estimated_premium ? formatPremium(put.estimated_premium) : "N/A"}
                              </p>
                            </div>
                            <div className="flex flex-col gap-1">
                              {put.unusual_activity && (
                                <TooltipProvider>
                                  <Tooltip>
                                    <TooltipTrigger>
                                      <Badge
                                        className={cn(
                                          "text-xs",
                                          getUnusualActivityColor(
                                            put.estimated_premium || 0,
                                            put.volume_to_oi_ratio || 0
                                          )
                                        )}
                                      >
                                        <AlertCircle className="h-3 w-3 mr-1" />
                                        Unusual
                                      </Badge>
                                    </TooltipTrigger>
                                    <TooltipContent>
                                      <p className="text-xs">{put.activity_reason}</p>
                                    </TooltipContent>
                                  </Tooltip>
                                </TooltipProvider>
                              )}
                              {put.flow_pattern && put.flow_pattern !== "isolated" && (
                                <Badge
                                  variant="outline"
                                  className={cn("text-xs", getFlowPatternColor(put.flow_pattern))}
                                >
                                  {put.flow_pattern}
                                </Badge>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Event Study Analysis */}
          {selectedSymbol && (
            <div className="mt-6">
              <h2 className="text-lg font-semibold mb-4">Event Study Analysis: {selectedSymbol}</h2>
              <EventStudy symbol={selectedSymbol} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
