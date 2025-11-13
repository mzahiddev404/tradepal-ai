/**
 * Chat header component
 * Displays title, description, and action buttons
 */
import { Button } from "@/components/ui/button";
import { FileText, TrendingUp, AlertTriangle } from "lucide-react";
import Link from "next/link";
import { MarketTime } from "./market-time";

interface ChatHeaderProps {
  showUpload: boolean;
  onToggleUpload: () => void;
  error?: string | null;
}

export function ChatHeader({ showUpload, onToggleUpload, error }: ChatHeaderProps) {
  return (
    <div className="border-b border-slate-200 bg-gradient-to-r from-slate-50 to-white px-4 py-4 sm:px-6 sm:py-5">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 shadow-md">
              <svg
                className="h-5 w-5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-slate-900">
                TradePal AI
              </h1>
              <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
                Your intelligent trading assistant
              </p>
            </div>
          </div>
          <MarketTime />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Link href="/market">
            <Button
              variant="outline"
              size="sm"
              className="h-9 border-slate-300 text-slate-700 hover:bg-green-50 hover:text-green-700 hover:border-green-300 transition-colors"
              aria-label="View market data"
            >
              <TrendingUp className="mr-2 h-3.5 w-3.5" aria-hidden="true" />
              Market
            </Button>
          </Link>
          <Link href="/disclaimer">
            <Button
              variant="outline"
              size="sm"
              className="h-9 border-slate-300 text-slate-700 hover:bg-amber-50 hover:text-amber-700 hover:border-amber-300 transition-colors"
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
                ? "bg-blue-600 hover:bg-blue-700 text-white shadow-sm"
                : "border-slate-300 text-slate-700 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-300"
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
          className="mt-4 rounded-md bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-800"
          role="alert"
          aria-live="polite"
        >
          {error}
        </div>
      )}
    </div>
  );
}

