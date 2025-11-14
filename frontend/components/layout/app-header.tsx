"use client";

/**
 * App Header Component
 * 
 * Consistent navigation header used across all pages.
 * Provides uniform navigation experience throughout the application.
 */

import { Button } from "@/components/ui/button";
import { TrendingUp, AlertTriangle, Settings, MessageSquare, GitCompare, Home } from "lucide-react";
import Link from "next/link";
import { MarketTime } from "@/components/chat/market-time";
import { cn } from "@/lib/utils";
import { usePathname } from "next/navigation";

type ChatMode = "standard" | "multi-llm";

interface AppHeaderProps {
  chatMode?: ChatMode;
  onModeChange?: (mode: ChatMode) => void;
  showDocuments?: boolean;
  onToggleDocuments?: () => void;
  error?: string | null;
}

export function AppHeader({
  chatMode,
  onModeChange,
  showDocuments = false,
  onToggleDocuments,
  error,
}: AppHeaderProps) {
  const pathname = usePathname();
  const isChatPage = pathname === "/" || pathname === "/compare";
  const isMarketPage = pathname === "/market";
  const isSettingsPage = pathname === "/settings";
  const isDisclaimerPage = pathname === "/disclaimer";

  return (
    <div className="trading-panel-header border-b border-[#2d3237] bg-gradient-to-b from-[#23272c] to-[#1a1e23] px-4 py-3 sm:px-6 sm:py-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
          <Link href="/" className="flex items-center gap-3">
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
          </Link>
          <MarketTime />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {/* Standard/Compare buttons - Toggle on chat pages, Links on non-chat pages */}
          {isChatPage && onModeChange ? (
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
          ) : (
            <>
              <Link href="/">
                <Button
                  variant={pathname === "/" ? "default" : "outline"}
                  size="sm"
                  className={cn(
                    "h-9 transition-colors",
                    pathname === "/"
                      ? "btn-trading-primary"
                      : "btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#007aff] hover:text-[#007aff]"
                  )}
                  aria-label="Standard chat mode"
                >
                  <MessageSquare className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
                  Standard
                </Button>
              </Link>
              <Link href="/compare">
                <Button
                  variant={pathname === "/compare" ? "default" : "outline"}
                  size="sm"
                  className={cn(
                    "h-9 transition-colors",
                    pathname === "/compare"
                      ? "btn-trading-primary"
                      : "btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#34c759] hover:text-[#34c759]"
                  )}
                  aria-label="Multi-LLM comparison mode"
                >
                  <GitCompare className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
                  Compare
                </Button>
              </Link>
            </>
          )}

          {/* Market Button */}
          <Link href="/market">
            <Button
              variant={isMarketPage ? "default" : "outline"}
              size="sm"
              className={cn(
                "h-9 transition-colors",
                isMarketPage
                  ? "btn-trading-primary"
                  : "btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#34c759] hover:text-[#34c759]"
              )}
              aria-label="View market data"
            >
              <TrendingUp className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
              Market
            </Button>
          </Link>

          {/* Settings Button */}
          <Link href="/settings">
            <Button
              variant={isSettingsPage ? "default" : "outline"}
              size="sm"
              className={cn(
                "h-9 transition-colors",
                isSettingsPage
                  ? "btn-trading-primary"
                  : "btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#34c759] hover:text-[#34c759]"
              )}
              aria-label="Open settings"
            >
              <Settings className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
              Settings
            </Button>
          </Link>

          {/* Disclaimer Button */}
          <Link href="/disclaimer">
            <Button
              variant={isDisclaimerPage ? "default" : "outline"}
              size="sm"
              className={cn(
                "h-9 transition-colors",
                isDisclaimerPage
                  ? "btn-trading-primary"
                  : "btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#ff9500] hover:text-[#ff9500]"
              )}
              aria-label="View disclaimer"
            >
              <AlertTriangle className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
              Disclaimer
            </Button>
          </Link>

          {/* Documents Button - Show on all pages */}
          {isChatPage && onToggleDocuments ? (
            <Button
              variant={showDocuments ? "default" : "outline"}
              size="sm"
              onClick={onToggleDocuments}
              className={`h-9 transition-colors ${
                showDocuments
                  ? "btn-trading-primary"
                  : "btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#007aff] hover:text-[#007aff]"
              }`}
              aria-label={showDocuments ? "Close document upload" : "Open document upload"}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="mr-2 h-3.5 w-3.5"
                aria-hidden="true"
              >
                <path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"></path>
                <path d="M14 2v5a1 1 0 0 0 1 1h5"></path>
                <path d="M10 9H8"></path>
                <path d="M16 13H8"></path>
                <path d="M16 17H8"></path>
              </svg>
              Documents
            </Button>
          ) : (
            <Link href="/">
              <Button
                variant="outline"
                size="sm"
                className="h-9 btn-trading border-[#373d41] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#007aff] hover:text-[#007aff] transition-colors"
                aria-label="Go to chat for document upload"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="mr-2 h-3.5 w-3.5"
                  aria-hidden="true"
                >
                  <path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"></path>
                  <path d="M14 2v5a1 1 0 0 0 1 1h5"></path>
                  <path d="M10 9H8"></path>
                  <path d="M16 13H8"></path>
                  <path d="M16 17H8"></path>
                </svg>
                Documents
              </Button>
            </Link>
          )}
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

