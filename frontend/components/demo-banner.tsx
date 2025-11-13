"use client";

import { AlertTriangle } from "lucide-react";
import Link from "next/link";

export function DemoBanner() {
  return (
    <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-b border-amber-200">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-amber-100 shrink-0">
            <AlertTriangle className="h-3.5 w-3.5 text-amber-700" />
          </div>
          <p className="text-xs sm:text-sm text-amber-900 leading-relaxed font-medium">
            <span className="font-semibold">Demo Application:</span> For educational purposes only. Not for actual trading decisions.{" "}
            <Link 
              href="/disclaimer" 
              className="underline font-semibold hover:text-amber-800 transition-colors"
            >
              See Disclaimer
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}


