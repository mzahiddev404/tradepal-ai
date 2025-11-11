"use client";

import { AlertTriangle } from "lucide-react";
import Link from "next/link";

export function DemoBanner() {
  return (
    <div className="bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-950/30 dark:to-amber-950/20 border-b border-yellow-200/50 dark:border-yellow-900/50 shadow-sm">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 flex-1">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-500" />
            </div>
            <p className="text-sm text-yellow-900 dark:text-yellow-100 leading-relaxed">
              <strong className="font-semibold">Demo Application:</strong> This is a demonstration app for educational
              purposes only. Not for actual trading or investment decisions.{" "}
              <Link 
                href="/disclaimer" 
                className="underline font-semibold hover:text-yellow-800 dark:hover:text-yellow-400 transition-colors"
              >
                See Disclaimer
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}


