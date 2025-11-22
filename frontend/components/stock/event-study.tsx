"use client";

import { useState, useEffect } from "react";
import { Card, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { getEventStudy, EventStudyResponse } from "@/lib/stock-api";
import { cn } from "@/lib/utils";
import { FileText, Network, Zap, RefreshCw, TrendingUp, TrendingDown, Activity, AlertTriangle, Gauge } from "lucide-react";

interface EventStudyProps {
  symbol: string;
  startDate?: string;
  endDate?: string;
  windows?: string;
}

export function EventStudy({ symbol, startDate, endDate, windows }: EventStudyProps) {
  const [data, setData] = useState<EventStudyResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getEventStudy(symbol, startDate, endDate, windows);
      if (result.error) {
        setError(result.error);
      } else {
        setData(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch event study data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (symbol) {
      fetchData();
    }
  }, [symbol, startDate, endDate, windows]);

  const formatCurrency = (val: number) => {
    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`;
    if (val >= 1000) return `$${(val / 1000).toFixed(0)}K`;
    return `$${val}`;
  };

  // RENDER
  return (
    <Card className="trading-panel p-0 border border-[#2d3237] bg-[#1a1e23] overflow-hidden">
        {/* Header with Knowledge Base Badge */}
        <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/5">
            <div>
                <CardTitle className="text-sm font-bold text-[#dcdcdc] uppercase tracking-widest flex items-center gap-2">
                    <Network className="h-4 w-4 text-[#34c759]" />
                    Smart Flow Analysis
                </CardTitle>
                <p className="text-[10px] text-gray-500 font-mono mt-1">
                    Parsing institutional order flow for directional bias
                </p>
            </div>
            <div className="flex flex-col items-end gap-1">
                <div className="flex items-center gap-2">
                    <Button 
                        variant="ghost" 
                        size="icon" 
                        onClick={() => fetchData()}
                        disabled={loading}
                        className="h-6 w-6 text-gray-500 hover:text-[#34c759]"
                        title="Refresh Analysis"
                    >
                        <RefreshCw className={cn("h-3.5 w-3.5", loading && "animate-spin")} />
                    </Button>
                    <Badge variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/20 text-[10px] h-5 px-2">
                        <FileText className="w-3 h-3 mr-1" />
                        LINKED: KNOWLEDGE BASE
                    </Badge>
                </div>
                <span className="text-[9px] text-gray-500 font-mono uppercase tracking-wider flex items-center">
                    <Zap className="h-2 w-2 mr-1 text-[#34c759]" />
                    Storage: Persistent
                </span>
            </div>
        </div>

        {/* Content Body */}
        <div className="p-4">
            {loading ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-4">
                  <Spinner />
                  <div className="text-center space-y-1">
                    <p className="text-[#dcdcdc] font-mono text-xs animate-pulse">Initializing Neural Flow Engine...</p>
                    <p className="text-gray-600 text-[10px]">Parsing options chain artifacts...</p>
                  </div>
                </div>
            ) : error || !data?.flow_report ? (
                 // Error state with Instructions
                 <div className="text-center py-8 space-y-3">
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-white/5 mb-2 border border-white/5">
                        <FileText className="h-5 w-5 text-gray-500" />
                    </div>
                    <h3 className="text-[#dcdcdc] font-mono text-sm font-bold tracking-wider">AWAITING DATA INGESTION</h3>
                    <div className="text-xs text-gray-500 max-w-xs mx-auto font-mono space-y-2 text-left bg-black/20 p-3 rounded border border-white/5">
                        <p className="text-gray-400 border-b border-white/5 pb-1 mb-2 font-bold">OPERATIONAL PROTOCOL:</p>
                        <p>1. Upload PDF/CSV (Option Flow) to Knowledge Base.</p>
                        <p>2. System extracts 'Flow Events' for {symbol}.</p>
                        <p>3. Click Refresh to run analysis.</p>
                    </div>
                    {error && <p className="text-red-500 text-xs mt-2">{error}</p>}
                 </div>
            ) : (
                <div className="space-y-6">
                    {/* 1. Main Bias Header */}
                    <div className="flex items-center justify-between p-4 rounded-lg border border-white/5 bg-gradient-to-r from-white/5 to-transparent">
                        <div>
                            <div className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mb-1">Flow Bias</div>
                            <div className={cn(
                                "text-2xl font-bold font-mono flex items-center gap-2",
                                data.flow_report.bias === "BULLISH" ? "text-[#34c759]" :
                                data.flow_report.bias === "BEARISH" ? "text-[#ff3b30]" : "text-yellow-500"
                            )}>
                                {data.flow_report.bias}
                                {data.flow_report.bias === "BULLISH" ? <TrendingUp className="h-6 w-6" /> : 
                                 data.flow_report.bias === "BEARISH" ? <TrendingDown className="h-6 w-6" /> : 
                                 <Activity className="h-6 w-6" />}
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mb-1">Flow Score</div>
                            <div className="text-xl font-mono text-[#dcdcdc]">{data.flow_report.flow_score.toFixed(2)}</div>
                        </div>
                        <div className="text-right">
                            <div className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mb-1">Conviction</div>
                            <Badge variant="outline" className={cn(
                                "border-0 text-xs font-bold",
                                data.flow_report.aggression_ratio > 0.6 ? "bg-[#34c759]/20 text-[#34c759]" : "bg-gray-500/20 text-gray-400"
                            )}>
                                {data.flow_report.conviction}
                            </Badge>
                        </div>
                    </div>

                    {/* 2. Metrics Grid */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 rounded border border-white/5 bg-black/20">
                            <div className="text-[10px] text-gray-500 uppercase mb-2">Net Premium</div>
                            <div className="flex justify-between items-end mb-1">
                                <span className="text-xs text-[#34c759]">Calls</span>
                                <span className="text-sm font-mono text-[#dcdcdc]">{formatCurrency(data.flow_report.call_premium)}</span>
                            </div>
                            <div className="flex justify-between items-end">
                                <span className="text-xs text-[#ff3b30]">Puts</span>
                                <span className="text-sm font-mono text-[#dcdcdc]">{formatCurrency(data.flow_report.put_premium)}</span>
                            </div>
                            {/* Mini Bar Chart */}
                            <div className="mt-2 h-1.5 w-full bg-[#2d3237] rounded-full overflow-hidden flex">
                                <div 
                                    className="h-full bg-[#34c759]" 
                                    style={{ width: `${(data.flow_report.call_premium / (data.flow_report.call_premium + data.flow_report.put_premium || 1)) * 100}%` }}
                                />
                                <div 
                                    className="h-full bg-[#ff3b30]" 
                                    style={{ width: `${(data.flow_report.put_premium / (data.flow_report.call_premium + data.flow_report.put_premium || 1)) * 100}%` }}
                                />
                            </div>
                        </div>

                        <div className="p-3 rounded border border-white/5 bg-black/20">
                            <div className="text-[10px] text-gray-500 uppercase mb-2">Aggression Ratio</div>
                            <div className="flex items-center justify-between mb-2">
                                <Gauge className="h-4 w-4 text-blue-400" />
                                <span className="text-xl font-mono text-[#dcdcdc]">{Math.round(data.flow_report.aggression_ratio * 100)}%</span>
                            </div>
                            <p className="text-[9px] text-gray-600">
                                % of sweeps executing at Ask or Above (Sign of urgency)
                            </p>
                        </div>
                    </div>

                    {/* 3. Key Insights */}
                    <div className="space-y-2">
                        <h4 className="text-xs font-bold text-[#dcdcdc] uppercase tracking-wide flex items-center gap-2">
                            <Activity className="h-3 w-3 text-[#007aff]" />
                            Flow Profile
                        </h4>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                            <div className="p-2 bg-white/5 rounded border border-white/5">
                                <span className="text-gray-500 block mb-1">Dominant Expiry</span>
                                <span className="font-mono text-[#dcdcdc]">{data.flow_report.dominant_expiry}</span>
                            </div>
                            {/* Placeholder for Top Strikes if we had them parsed */}
                            {/* 
                            <div className="p-2 bg-white/5 rounded border border-white/5">
                                <span className="text-gray-500 block mb-1">Top Strikes</span>
                                <span className="font-mono text-[#dcdcdc]">--</span>
                            </div> 
                            */}
                        </div>
                    </div>

                    {/* 4. Recommendation */}
                    <div className="p-3 rounded bg-blue-500/5 border border-blue-500/20">
                        <div className="flex items-start gap-2">
                            <AlertTriangle className="h-4 w-4 text-blue-400 mt-0.5" />
                            <div>
                                <div className="text-[10px] font-bold text-blue-400 uppercase tracking-wide mb-1">AI Recommendation</div>
                                <p className="text-xs text-[#dcdcdc] leading-relaxed font-mono">
                                    {data.flow_report.recommendation}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    </Card>
  );
}
