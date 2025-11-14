/**
 * Chat header component
 * Displays title, description, and action buttons
 */
import { Button } from "@/components/ui/button";
import { FileText, TrendingUp, AlertTriangle, Settings, MessageSquare, GitCompare } from "lucide-react";
import Link from "next/link";
import { MarketTime } from "./market-time";
import { cn } from "@/lib/utils";

type ChatMode = "standard" | "multi-llm";

interface ChatHeaderProps {
  showUpload: boolean;
  onToggleUpload: () => void;
  error?: string | null;
  chatMode?: ChatMode;
  onModeChange?: (mode: ChatMode) => void;
}

export function ChatHeader({ showUpload, onToggleUpload, error, chatMode = "standard", onModeChange }: ChatHeaderProps) {
  return (
    <div className="trading-panel-header border-b border-[#2d3237] bg-gradient-to-b from-[#23272c] to-[#1a1e23] px-4 py-3 sm:px-6 sm:py-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-md bg-gradient-to-br from-[#34c759] to-[#28a745] border-2 border-[#28a745] shadow-lg">
              <svg
                className="h-6 w-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2.5}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-[#dcdcdc] tracking-tight">
                TRADEPAL
              </h1>
              <p className="text-xs sm:text-sm text-[#34c759] mt-0.5 uppercase tracking-wider font-semibold">
                Trading Education & Pattern Analysis
              </p>
            </div>
          </div>
          <MarketTime />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {onModeChange && (
            <>
              <Button
                variant={chatMode === "standard" ? "default" : "outline"}
                size="sm"
                onClick={() => onModeChange("standard")}
                className={cn(
                  "h-9 transition-colors",
                  chatMode === "standard"
                    ? "btn-trading-primary"
                    : "btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#007aff] hover:text-[#007aff]"
                )}
                aria-label="Standard chat mode"
              >
                <MessageSquare className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
                Standard
              </Button>
              <Button
                variant={chatMode === "multi-llm" ? "default" : "outline"}
                size="sm"
                onClick={() => onModeChange("multi-llm")}
                className={cn(
                  "h-9 transition-colors",
                  chatMode === "multi-llm"
                    ? "btn-trading-primary"
                    : "btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#34c759] hover:text-[#34c759]"
                )}
                aria-label="Multi-LLM comparison mode"
              >
                <GitCompare className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
                Compare
              </Button>
            </>
          )}
          <Link href="/market">
            <Button
              variant="outline"
              size="sm"
              className="h-9 btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#34c759] hover:text-[#34c759] transition-colors"
              aria-label="View market data"
            >
              <TrendingUp className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
              Market
            </Button>
          </Link>
          <Link href="/settings">
            <Button
              variant="outline"
              size="sm"
              className="h-9 btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#34c759] hover:text-[#34c759] transition-colors"
              aria-label="Open settings"
            >
              <Settings className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
              Settings
            </Button>
          </Link>
          <Link href="/disclaimer">
            <Button
              variant="outline"
              size="sm"
              className="h-9 btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#ff9500] hover:text-[#ff9500] transition-colors"
              aria-label="View disclaimer"
            >
              <AlertTriangle className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
              Disclaimer
            </Button>
          </Link>
          <Button
            variant={showUpload ? "default" : "outline"}
            size="sm"
            onClick={onToggleUpload}
            className={`h-9 transition-colors ${
              showUpload
                ? "btn-trading-primary"
                : "btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#007aff] hover:text-[#007aff]"
            }`}
            aria-label={showUpload ? "Close document upload" : "Open document upload"}
          >
            <FileText className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
            Documents
          </Button>
        </div>
      </div>
      {error && (
        <div
          className="mt-4 rounded border border-[#ff3b30] bg-[#2d1f1f] px-4 py-3 text-sm text-[#ff6b6b]"
          role="alert"
          aria-live="polite"
        >
          {error}
        </div>
      )}
    </div>
  );
}

