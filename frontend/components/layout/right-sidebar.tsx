"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { Activity, ChevronRight, ChevronLeft, WifiOff, TrendingUp, Database, Info } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";

interface CryptoPrice {
  id: string;
  symbol: string;
  name: string;
  priceUsd: string;
  changePercent24Hr: string;
}

interface StockQuote {
  symbol: string;
  name: string;
  current_price: number;
  change: number;
  change_percent: number;
  timestamp: string;
  source?: string;
  error?: string;
}

export function RightSidebar() {
  const [isOpen, setIsOpen] = useState(true);
  const [stockData, setStockData] = useState<StockQuote[]>([]);
  const [stockLoading, setStockLoading] = useState(true);
  const [stockError, setStockError] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>("");
  const [latency, setLatency] = useState<number>(0);
  const [apiUsage, setApiUsage] = useState<any>(null);
  const [marketStatus, setMarketStatus] = useState({ status: "CLOSED", color: "text-[#ff3b30]" });

  // Format date to Eastern Time
  const formatEasternTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      timeZone: "America/New_York",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true // AM/PM
    }) + " EST";
  };

  // Helper to determine Market Status based on ET
  const getMarketStatus = () => {
    const now = new Date();
    // Convert current time to ET
    const etTime = new Date(now.toLocaleString("en-US", { timeZone: "America/New_York" }));
    const day = etTime.getDay(); // 0 = Sun, 6 = Sat
    const hour = etTime.getHours();
    const minute = etTime.getMinutes();
    const timeInMinutes = hour * 60 + minute;

    // Weekend
    if (day === 0 || day === 6) return { status: "CLOSED", color: "text-[#ff3b30]" };

    // Market Hours: 9:30 AM - 4:00 PM ET (570 - 960 minutes)
    const marketOpen = 9 * 60 + 30;
    const marketClose = 16 * 60;

    if (timeInMinutes >= marketOpen && timeInMinutes < marketClose) {
        return { status: "OPEN", color: "text-[#34c759]" };
    } else if (timeInMinutes >= (4 * 60) && timeInMinutes < marketOpen) {
         return { status: "PRE-MARKET", color: "text-yellow-500" };
    } else if (timeInMinutes >= marketClose && timeInMinutes < (20 * 60)) {
         return { status: "AFTER-HOURS", color: "text-yellow-500" };
    } else {
         return { status: "CLOSED", color: "text-[#ff3b30]" };
    }
  };

  // Fetch Live Stock Prices and API Usage
  useEffect(() => {
    const abortController = new AbortController();
    
    const fetchStocksAndLimits = async () => {
      const startTime = performance.now();
      try {
        setStockError(false);
        
        // 1. Fetch Stocks
        const stockResponse = await fetch("/api/stocks?symbols=SPY,QQQ,NVDA,TSLA,AAPL,MSFT,AMD,COIN,MSTR", {
          signal: abortController.signal
        });
        
        if (stockResponse.ok) {
            const data = await stockResponse.json();
            if (Array.isArray(data)) {
              setStockData(data);
              updateStatus(startTime);
            }
        } else {
            throw new Error("Failed to fetch stocks");
        }

        // 2. Fetch API Usage Limits (from our new endpoint)
        try {
            const limitsResponse = await fetch("/api/limits", {
                signal: abortController.signal
            });
            if (limitsResponse.ok) {
                const limitsData = await limitsResponse.json();
                setApiUsage(limitsData);
            }
        } catch (e) {
            console.warn("Failed to fetch API limits", e);
        }

      } catch (err: any) {
        if (err.name === 'AbortError') return;
        console.warn("Stock data fetch failed:", err.message);
        setStockError(true);
      } finally {
        setStockLoading(false);
      }
    };

    const updateStatus = (startTime: number) => {
        const now = new Date();
        setLastUpdated(`${now.toLocaleDateString("en-US", { timeZone: "America/New_York" })} ${formatEasternTime(now)}`);
        const endTime = performance.now();
        setLatency(Math.round(endTime - startTime));
        setMarketStatus(getMarketStatus());
    };

    fetchStocksAndLimits();
    // Update stocks every 30 seconds
    const interval = setInterval(fetchStocksAndLimits, 30000);
    
    return () => {
        clearInterval(interval);
        abortController.abort();
    };
  }, []);

  if (!isOpen) {
    return (
      <div className="hidden xl:flex flex-col h-full border-l border-white/5 bg-[#0F1115] w-12 items-center py-4 gap-4">
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={() => setIsOpen(true)}
          className="text-gray-400 hover:text-[#34c759] hover:bg-white/5"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <div className="writing-vertical-lr text-xs font-mono text-gray-500 tracking-widest uppercase flex items-center gap-2 rotate-180">
          <span>Market Intelligence</span>
          <Activity className="h-3 w-3" />
        </div>
      </div>
    );
  }

  // Helpers for API Usage Display
  const getUsageColor = (count: number, limit: number | string) => {
      if (limit === "Unlimited") return "text-[#34c759]";
      const percent = (count / (typeof limit === 'number' ? limit : 1)) * 100;
      if (percent > 90) return "text-[#ff3b30]";
      if (percent > 70) return "text-yellow-500";
      return "text-[#34c759]";
  };

  return (
    <aside className="hidden xl:flex flex-col w-80 h-full glass-panel border-l border-white/5 bg-[#131619]/80 backdrop-blur-xl relative overflow-hidden transition-all duration-300">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/5 bg-white/5">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-[#34c759]" />
          <h2 className="text-xs font-bold text-[#dcdcdc] uppercase tracking-widest">Market Intel</h2>
        </div>
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={() => setIsOpen(false)}
          className="h-6 w-6 text-gray-400 hover:text-white"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-6">
        
        {/* Live Equities Ticker */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Link href="/market" className="group flex items-center gap-2 cursor-pointer">
                <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest group-hover:text-[#34c759] transition-colors">Equities</h3>
                <TrendingUp className="h-3 w-3 text-[#007aff] group-hover:text-[#34c759] transition-colors" />
            </Link>
            <Link href="/market" className="text-[9px] text-gray-600 hover:text-[#34c759] transition-colors font-mono">
                VIEW ALL →
            </Link>
          </div>

          <div className="space-y-2">
            {stockLoading && stockData.length === 0 ? (
               <div className="text-xs text-gray-500 font-mono text-center py-4">Loading Stocks...</div>
            ) : stockError ? (
               <div className="text-xs text-yellow-500 font-mono text-center py-2">Market Data Unavailable</div>
            ) : (
              stockData.map((stock) => {
                const isPositive = stock.change >= 0;
                return (
                  <div key={stock.symbol} className="flex flex-col gap-1 p-2 rounded border border-white/5 bg-white/5 hover:bg-white/10 transition-colors group cursor-default">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className={cn(
                            "w-1 h-8 rounded-full transition-colors",
                            isPositive ? "bg-[#34c759]" : "bg-[#ff3b30]"
                          )}></div>
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span className="text-xs font-bold text-[#dcdcdc]">{stock.symbol}</span>
                              <span className="text-[10px] text-gray-500 truncate max-w-[100px]">{stock.name}</span>
                            </div>
                            <div className="text-[10px] text-gray-400 font-mono">
                              ${stock.current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </div>
                          </div>
                        </div>
                        <div className={cn(
                          "text-[10px] font-bold font-mono px-1.5 py-0.5 rounded",
                          isPositive ? "text-[#34c759] bg-[#34c759]/10" : "text-[#ff3b30] bg-[#ff3b30]/10"
                        )}>
                          {isPositive ? "+" : ""}{stock.change_percent.toFixed(2)}%
                        </div>
                    </div>
                    {stock.source && (
                        <div className="flex justify-end">
                            <span className="text-[8px] text-gray-600 font-mono uppercase tracking-wider">
                                Source: {stock.source}
                            </span>
                        </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
          
          {lastUpdated && (
            <div className="flex items-center justify-end gap-1.5 mt-2">
              {stockError && <WifiOff className="h-3 w-3 text-yellow-500" />}
              <div className="text-[9px] text-gray-600 font-mono text-right">
                {lastUpdated}
              </div>
            </div>
          )}
        </div>

        {/* API Usage & System Status */}
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">System Status</h3>
                <Database className="h-3 w-3 text-gray-500" />
            </div>
            
            <div className="p-3 rounded border border-dashed border-white/10 bg-white/5 space-y-2">
                <div className="flex items-center justify-between">
                    <span className="text-[10px] text-gray-500 uppercase">API Latency</span>
                    <span className={cn(
                        "text-[10px] font-mono",
                        latency > 500 ? "text-yellow-500" : "text-[#34c759]"
                    )}>{latency > 0 ? `${latency}ms` : '...'}</span>
                </div>
                <div className="flex items-center justify-between">
                    <span className="text-[10px] text-gray-500 uppercase">Market Status</span>
                    <span className={cn("text-[10px] font-mono", marketStatus.color)}>{marketStatus.status}</span>
                </div>
                
                {/* API Usage Stats */}
                {apiUsage && (
                    <div className="pt-2 mt-2 border-t border-white/5 space-y-1">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1">
                                <span className="text-[10px] text-gray-500 uppercase">Alpha Vantage</span>
                                <TooltipProvider>
                                    <Tooltip>
                                        <TooltipTrigger>
                                            <Info className="h-2.5 w-2.5 text-gray-600" />
                                        </TooltipTrigger>
                                        <TooltipContent>
                                            <p>Daily limit for free Alpha Vantage API tier</p>
                                        </TooltipContent>
                                    </Tooltip>
                                </TooltipProvider>
                            </div>
                            <span className={cn(
                                "text-[10px] font-mono",
                                getUsageColor(apiUsage.alpha_vantage.count, apiUsage.alpha_vantage.limit)
                            )}>
                                {apiUsage.alpha_vantage.count}/{apiUsage.alpha_vantage.limit}
                            </span>
                        </div>
                        
                        <div className="flex items-center justify-between">
                            <span className="text-[10px] text-gray-500 uppercase">Yahoo Finance</span>
                            <span className="text-[10px] text-[#34c759] font-mono">
                                {apiUsage.yfinance.count} (Unl.)
                            </span>
                        </div>
                    </div>
                )}
            </div>
        </div>

      </div>
    </aside>
  );
}
