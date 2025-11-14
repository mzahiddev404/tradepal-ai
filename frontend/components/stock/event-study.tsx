"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { ErrorMessage } from "@/components/ui/error-message";
import { getEventStudy, EventStudyResponse } from "@/lib/stock-api";
import { cn } from "@/lib/utils";

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

  useEffect(() => {
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

    if (symbol) {
      fetchData();
    }
  }, [symbol, startDate, endDate, windows]);

  if (loading) {
    return (
      <Card className="trading-panel p-6 border border-[#2d3237] bg-[#1a1e23]">
        <div className="flex items-center justify-center py-8">
          <Spinner />
          <span className="ml-2 text-[#dcdcdc]">Loading event study analysis...</span>
        </div>
      </Card>
    );
  }

  // Show research insights even if there's an error or no calculated data
  const hasResearchInsights = data?.research_insights && Object.keys(data.research_insights).length > 0;
  const hasCalculatedData = data?.summary && data.summary.length > 0;

  if (error && !hasResearchInsights) {
    return (
      <Card className="trading-panel p-6 border border-[#ff3b30] bg-[#2d1f1f]">
        <ErrorMessage message={error || "Unknown error"} />
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className="trading-panel p-6 border border-[#2d3237] bg-[#1a1e23]">
        <p className="text-[#969696]">No data available.</p>
      </Card>
    );
  }

  // Group summary by holiday (if calculated data exists)
  const groupedByHoliday = hasCalculatedData ? data.summary!.reduce((acc, item) => {
      if (!acc[item.holiday]) {
        acc[item.holiday] = [];
      }
      acc[item.holiday]!.push(item);
    return acc;
  }, {} as Record<string, typeof data.summary>) : {};

  // Format holiday names for display
  const formatHolidayName = (name: string) => {
    return name
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(" ");
  };

  // Determine significance badge
  const getSignificanceBadge = (pValue: number) => {
    if (pValue < 0.01) {
      return <Badge className="bg-red-500">***</Badge>;
    } else if (pValue < 0.05) {
      return <Badge className="bg-orange-500">**</Badge>;
    } else if (pValue < 0.1) {
      return <Badge className="bg-yellow-500">*</Badge>;
    }
    return <Badge variant="outline">ns</Badge>;
  };

  return (
    <Card className="trading-panel p-6 border border-[#2d3237] bg-[#1a1e23]">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-[#dcdcdc] uppercase tracking-tight">Holiday Correlation Analysis: {data.symbol}</h2>
          {data.start_date && data.end_date && (
            <p className="text-sm text-[#969696] mt-1 trading-number">
              Period: {new Date(data.start_date).toLocaleDateString()} -{" "}
              {new Date(data.end_date).toLocaleDateString()}
            </p>
          )}
          {data.error && (
            <div className="mt-2 p-3 bg-[#2d1f1f] border border-[#ff3b30] rounded">
              <p className="text-sm text-[#ff6b6b]">{data.error}</p>
            </div>
          )}
        </div>

        {/* Research-Based Insights */}
        {hasResearchInsights && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-3 text-[#007aff] uppercase tracking-wide">
                📊 Research-Based Historical Correlations
              </h3>
              <p className="text-sm text-[#969696] mb-4">
                Based on academic research from 1928-2024 across major markets (U.S., U.K., Japan)
              </p>
            </div>

            {data.research_insights && Object.entries(data.research_insights).map(([holidayKey, insights]: [string, any]) => (
              <div key={holidayKey} className="border border-[#2d3237] rounded p-4 bg-[#23272c]">
                <h4 className="font-semibold mb-2 text-[#007aff]">{insights.holiday}</h4>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-[#dcdcdc] uppercase tracking-wide">Effect Type:</p>
                    <p className="text-sm text-[#969696]">{insights.effect_type}</p>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium text-[#dcdcdc] uppercase tracking-wide">Historical Performance:</p>
                    <ul className="text-sm text-[#969696] list-disc list-inside space-y-1 mt-1">
                      {Object.entries(insights.historical_performance).map(([period, perf]: [string, any]) => (
                        <li key={period}>
                          <span className="font-medium capitalize">{period.replace('_', ' ')}:</span> {perf}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-[#dcdcdc] uppercase tracking-wide">Key Research Findings:</p>
                    <ul className="text-sm text-[#969696] list-disc list-inside space-y-1 mt-1">
                      {insights.key_findings.map((finding: string, idx: number) => (
                        <li key={idx}>{finding}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="flex gap-2 text-xs">
                    <Badge variant="outline" className="border-[#2d3237] text-[#969696]">Research Period: {insights.research_period}</Badge>
                    <Badge variant="outline" className="border-[#2d3237] text-[#969696]">Confidence: {insights.confidence_level}</Badge>
                  </div>
                </div>
              </div>
            ))}

            {/* General Findings */}
            {data.general_findings && data.general_findings.length > 0 && (
              <div className="border-t border-[#2d3237] pt-4 mt-4">
                <h4 className="font-semibold mb-2 text-[#dcdcdc] uppercase tracking-wide">General Holiday Effect Findings:</h4>
                <ul className="text-sm text-[#969696] list-disc list-inside space-y-1">
                  {data.general_findings.map((finding: string, idx: number) => (
                    <li key={idx}>{finding}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Disclaimers */}
            {data.disclaimers && data.disclaimers.length > 0 && (
              <div className="border-t border-[#2d3237] pt-4 mt-4">
                <h4 className="font-semibold mb-2 text-[#ff9500] uppercase tracking-wide">Important Disclaimers:</h4>
                <ul className="text-xs text-[#ffb84d] list-disc list-inside space-y-1">
                  {data.disclaimers.map((disclaimer: string, idx: number) => (
                    <li key={idx}>{disclaimer}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Calculated Data (if available) */}
        {hasCalculatedData && (
          <div className="space-y-4 border-t border-[#2d3237] pt-6">
            <h3 className="text-lg font-semibold text-[#dcdcdc] uppercase tracking-wide">Calculated Event Study Results</h3>

            {/* Summary Statistics by Holiday */}
            <div className="space-y-4">
              <h4 className="text-md font-semibold text-[#dcdcdc] uppercase tracking-wide">Summary Statistics by Holiday</h4>
              {Object.entries(groupedByHoliday).map(([holiday, items]) => (
            <div key={holiday} className="border border-[#2d3237] rounded p-4 bg-[#23272c]">
              <h4 className="font-semibold mb-3 text-[#007aff] uppercase tracking-wide">
                {formatHolidayName(holiday)}
              </h4>
              <div className="overflow-x-auto">
                <table className="trading-table w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#2d3237]">
                      <th className="text-left p-2 text-[#969696] uppercase tracking-wide">Window</th>
                      <th className="text-right p-2 text-[#969696] uppercase tracking-wide">Count</th>
                      <th className="text-right p-2 text-[#969696] uppercase tracking-wide">Mean Return</th>
                      <th className="text-right p-2 text-[#969696] uppercase tracking-wide">Std Dev</th>
                      <th className="text-right p-2 text-[#969696] uppercase tracking-wide">t-stat</th>
                      <th className="text-right p-2 text-[#969696] uppercase tracking-wide">p-value</th>
                      <th className="text-center p-2 text-[#969696] uppercase tracking-wide">Significance</th>
                    </tr>
                  </thead>
                    <tbody>
                      {items?.map((item, idx) => (
                      <tr key={idx} className="border-b border-[#2d3237] hover:bg-[#23272c]">
                        <td className="p-2 font-mono text-[#dcdcdc]">{item.window}</td>
                        <td className="text-right p-2 trading-number text-[#dcdcdc]">{item.count}</td>
                        <td
                          className={cn(
                            "text-right p-2 font-semibold trading-number",
                            item.mean > 0 ? "gain" : "loss"
                          )}
                        >
                          {(item.mean * 100).toFixed(4)}%
                        </td>
                        <td className="text-right p-2 trading-number text-[#dcdcdc]">{(item.std * 100).toFixed(4)}%</td>
                        <td className="text-right p-2 trading-number text-[#dcdcdc]">{item.t_stat?.toFixed(4) || "N/A"}</td>
                        <td className="text-right p-2 trading-number text-[#dcdcdc]">{item.bootstrap_p?.toFixed(4) || "N/A"}</td>
                        <td className="text-center p-2">
                          {item.bootstrap_p ? getSignificanceBadge(item.bootstrap_p) : "N/A"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div className="border-t border-[#2d3237] pt-4">
          <p className="text-xs text-[#969696]">
            <strong>Significance levels:</strong> *** p &lt; 0.01, ** p &lt; 0.05, * p &lt; 0.1, ns = not significant
          </p>
          <p className="text-xs text-[#969696] mt-1">
            <strong>Window format:</strong> Days relative to event (e.g., "-5..5" means 5 days before to 5 days after)
          </p>
        </div>

            {/* Event Details (Optional - can be collapsed) */}
            {data.events && data.events.length > 0 && (
          <details className="border-t border-[#2d3237] pt-4">
            <summary className="cursor-pointer font-semibold text-sm text-[#007aff] hover:text-[#34c759] uppercase tracking-wide">
              View Individual Event Returns ({data.events.length} events)
            </summary>
            <div className="mt-4 max-h-96 overflow-y-auto">
              <table className="trading-table w-full text-xs">
                <thead className="sticky top-0 bg-[#23272c]">
                  <tr className="border-b border-[#2d3237]">
                    <th className="text-left p-2 text-[#969696] uppercase tracking-wide">Holiday</th>
                    <th className="text-left p-2 text-[#969696] uppercase tracking-wide">Event Date</th>
                    <th className="text-left p-2 text-[#969696] uppercase tracking-wide">Window</th>
                    <th className="text-right p-2 text-[#969696] uppercase tracking-wide">Cumulative Return</th>
                  </tr>
                </thead>
                <tbody>
                  {data.events.map((event, idx) => (
                    <tr key={idx} className="border-b border-[#2d3237] hover:bg-[#23272c]">
                      <td className="p-2 text-[#dcdcdc]">{formatHolidayName(event.holiday)}</td>
                      <td className="p-2 trading-number text-[#dcdcdc]">{new Date(event.event_date).toLocaleDateString()}</td>
                      <td className="p-2 font-mono text-[#dcdcdc]">{event.window}</td>
                      <td
                        className={cn(
                          "text-right p-2 font-semibold trading-number",
                          event.cum_return && event.cum_return > 0
                            ? "gain"
                            : "loss"
                        )}
                      >
                        {event.cum_return !== null && event.cum_return !== undefined
                          ? `${(event.cum_return * 100).toFixed(4)}%`
                          : "N/A"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            </details>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}

