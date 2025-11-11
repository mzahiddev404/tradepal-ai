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
        const changeColor = isPositive ? "text-green-600" : "text-red-600";

        return (
          <Card key={index.symbol} className="p-4">
            <div className="space-y-2">
              <div>
                <h3 className="font-semibold">{index.symbol}</h3>
                <p className="text-xs text-muted-foreground">{index.name}</p>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-xl font-bold">
                  ${index.price.toFixed(2)}
                </span>
                <div className={cn("flex items-center gap-1 text-sm", changeColor)}>
                  {isPositive ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  <span>
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


