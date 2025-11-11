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
      <Card className="p-4">
        <p className="text-destructive">Error: {quote.error}</p>
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
    <Card className="p-6">
      <div className="space-y-4">
        <div>
          <h2 className="text-2xl font-bold">{quote.symbol}</h2>
          {quote.name && <p className="text-sm text-muted-foreground">{quote.name}</p>}
        </div>

        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold">
            ${quote.current_price?.toFixed(2) || "N/A"}
          </span>
          <div className={cn("flex items-center gap-1", changeColor)}>
            {isPositive && <TrendingUp className="h-4 w-4" />}
            {isNegative && <TrendingDown className="h-4 w-4" />}
            {!isPositive && !isNegative && <Minus className="h-4 w-4" />}
            <span className="font-semibold">
              {quote.change && quote.change > 0 ? "+" : ""}
              {quote.change?.toFixed(2) || "0.00"} (
              {quote.change_percent && quote.change_percent > 0 ? "+" : ""}
              {quote.change_percent?.toFixed(2) || "0.00"}%)
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
          <div>
            <p className="text-xs text-muted-foreground">Previous Close</p>
            <p className="font-semibold">${quote.previous_close?.toFixed(2) || "N/A"}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Volume</p>
            <p className="font-semibold">
              {quote.volume
                ? new Intl.NumberFormat().format(quote.volume)
                : "N/A"}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">52W High</p>
            <p className="font-semibold">${quote.high_52w?.toFixed(2) || "N/A"}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">52W Low</p>
            <p className="font-semibold">${quote.low_52w?.toFixed(2) || "N/A"}</p>
          </div>
        </div>
      </div>
    </Card>
  );
}


