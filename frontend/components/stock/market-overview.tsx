"use client";

import { Card } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";
import { MarketOverview } from "@/lib/stock-api";
import { cn } from "@/lib/utils";

interface MarketOverviewProps {
  overview: MarketOverview;
}

export function MarketOverviewDisplay({ overview }: MarketOverviewProps) {
  if (overview.error || !overview.indices) {
    return (
      <Card className="p-4">
        <p className="text-destructive">
          Error loading market data: {overview.error || "Unknown error"}
        </p>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {overview.indices.map((index) => {
        const isPositive = index.change_percent > 0;
        const changeColor = isPositive ? "gain" : "loss";

        return (
          <Card key={index.symbol} className="trading-panel p-4 border border-[#2d3237] bg-[#1a1e23]">
            <div className="space-y-2">
              <div>
                <h3 className="font-semibold text-[#dcdcdc] uppercase tracking-wide">{index.symbol}</h3>
                <p className="text-xs text-[#969696]">{index.name}</p>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-xl font-bold trading-number text-[#dcdcdc]">
                  ${index.price.toFixed(2)}
                </span>
                <div className={cn("flex items-center gap-1 text-sm font-medium", changeColor)}>
                  {isPositive ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  <span className="trading-number">
                    {index.change > 0 ? "+" : ""}
                    {index.change.toFixed(2)} (
                    {index.change_percent > 0 ? "+" : ""}
                    {index.change_percent.toFixed(2)}%)
                  </span>
                </div>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}


