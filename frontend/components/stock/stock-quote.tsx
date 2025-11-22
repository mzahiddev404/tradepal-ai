"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { StockQuote } from "@/lib/stock-api";
import { cn } from "@/lib/utils";

interface StockQuoteProps {
  quote: StockQuote;
}

export function StockQuoteDisplay({ quote }: StockQuoteProps) {
  if (quote.error) {
    return (
      <Card className="trading-panel p-4 border border-[#ff3b30] bg-[#2d1f1f]">
        <p className="text-[#ff6b6b]">Error: {quote.error}</p>
      </Card>
    );
  }

  const isPositive = (quote.change_percent || 0) > 0;
  const isNegative = (quote.change_percent || 0) < 0;
  const changeColor = isPositive
    ? "text-green-600"
    : isNegative
    ? "text-red-600"
    : "text-muted-foreground";

  return (
    <Card className="trading-panel p-6 border border-[#2d3237] bg-[#1a1e23]">
      <div className="space-y-4">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold text-[#dcdcdc] uppercase tracking-tight">{quote.symbol}</h2>
            {quote.name && <p className="text-sm text-[#969696]">{quote.name}</p>}
          </div>
          {quote.source && (
            <Badge variant="outline" className="text-[10px] text-[#969696] border-[#373d41]">
              Source: {quote.source}
            </Badge>
          )}
        </div>

        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold trading-number text-[#dcdcdc]">
            ${quote.current_price?.toFixed(2) || "N/A"}
          </span>
          <div className={cn("flex items-center gap-1 font-semibold", isPositive ? "gain" : isNegative ? "loss" : "text-[#969696]")}>
            {isPositive && <TrendingUp className="h-4 w-4" />}
            {isNegative && <TrendingDown className="h-4 w-4" />}
            {!isPositive && !isNegative && <Minus className="h-4 w-4" />}
            <span className="trading-number">
              {quote.change && quote.change > 0 ? "+" : ""}
              {quote.change?.toFixed(2) || "0.00"} (
              {quote.change_percent && quote.change_percent > 0 ? "+" : ""}
              {quote.change_percent?.toFixed(2) || "0.00"}%)
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-[#2d3237]">
          <div>
            <p className="text-xs text-[#969696] uppercase tracking-wide">Previous Close</p>
            <p className="font-semibold trading-number text-[#dcdcdc]">${quote.previous_close?.toFixed(2) || "N/A"}</p>
          </div>
          {quote.volume && quote.volume > 0 && (
            <div>
              <p className="text-xs text-[#969696] uppercase tracking-wide">Volume</p>
              <p className="font-semibold trading-number text-[#dcdcdc]">
                {new Intl.NumberFormat().format(quote.volume)}
              </p>
            </div>
          )}
          {quote.high_52w && quote.high_52w > 0 && (
            <div>
                <p className="text-xs text-[#969696] uppercase tracking-wide">52W High</p>
                <p className="font-semibold trading-number text-[#dcdcdc]">${quote.high_52w?.toFixed(2)}</p>
            </div>
          )}
          {quote.low_52w && quote.low_52w > 0 && (
            <div>
                <p className="text-xs text-[#969696] uppercase tracking-wide">52W Low</p>
                <p className="font-semibold trading-number text-[#dcdcdc]">${quote.low_52w?.toFixed(2)}</p>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
