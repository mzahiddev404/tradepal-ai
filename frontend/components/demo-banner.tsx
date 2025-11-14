"use client";

import { AlertTriangle } from "lucide-react";
import Link from "next/link";

export function DemoBanner() {
  return (
    <div className="bg-gradient-to-r from-[#2d2419] to-[#3d2e1f] border-b border-[#4a3a2a]">
      <div className="container mx-auto px-4 py-2.5">
        <div className="flex items-center gap-3">
          <div className="flex h-5 w-5 items-center justify-center rounded bg-[#ff9500]/20 border border-[#ff9500]/30 shrink-0">
            <AlertTriangle className="h-3 w-3 text-[#ff9500]" />
          </div>
          <p className="text-xs sm:text-sm text-[#ffb84d] leading-relaxed font-medium uppercase tracking-wide">
            <span className="font-semibold">Demo Application:</span> For educational purposes only. Not for actual trading decisions.{" "}
            <Link 
              href="/disclaimer" 
              className="underline font-semibold hover:text-[#ffcc80] transition-colors"
            >
              See Disclaimer
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}


