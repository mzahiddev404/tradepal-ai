"use client";

/**
 * Compare Page
 * 
 * Dedicated page for multi-LLM comparison feature.
 * Provides a full-screen comparison view.
 */

import { MultiLLMComparison } from "@/components/chat/multi-llm-comparison";
import { ErrorBoundary } from "@/components/error-boundary";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { MarketTime } from "@/components/chat/market-time";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";

type ChatMode = "standard" | "multi-llm";

export default function ComparePage() {
  const router = useRouter();
  const [chatMode, setChatMode] = useState<ChatMode>("multi-llm");
  const [showUpload, setShowUpload] = useState(false);

  const handleModeChange = (mode: ChatMode) => {
    if (mode === "standard") {
      // Navigate to home page
      router.push("/");
    } else {
      // Already on compare page
      setChatMode(mode);
    }
  };

  const handleToggleUpload = () => {
    // If they want to upload, they should probably go to standard chat or we implement it here?
    // For now, redirect to standard chat for upload
    router.push("/");
  };

  return (
    <div className="flex h-screen w-full bg-[#0F1115] bg-grid-subtle text-[#dcdcdc] overflow-hidden">
      {/* Sidebar */}
      <AppSidebar 
        chatMode={chatMode} 
        onModeChange={handleModeChange}
        showDocuments={false}
        onToggleDocuments={handleToggleUpload}
      />

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="h-14 border-b border-white/5 flex items-center justify-between px-4 sm:px-6 bg-[#131619]/50 backdrop-blur-sm shrink-0 z-10">
           <div className="flex items-center gap-3 md:hidden">
             <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-gradient-to-br from-[#34c759] to-[#28a745]">
               <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
               </svg>
             </div>
             <span className="font-bold text-white tracking-tight">TRADEPAL</span>
          </div>

          <div className="hidden md:flex items-center text-sm font-medium text-gray-400">
             <span className="text-gray-500">Workspace</span>
             <span className="mx-2">/</span>
             <span className="text-white">Model Comparison</span>
          </div>

          <div className="flex items-center gap-4">
            <MarketTime />
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 p-4 sm:p-6 md:p-8 overflow-hidden relative">
          <div className="max-w-7xl mx-auto h-full flex flex-col">
            <ErrorBoundary>
              <div className="flex-1 h-full glass-panel rounded-lg overflow-hidden flex flex-col">
                <MultiLLMComparison />
              </div>
            </ErrorBoundary>
          </div>
        </div>
      </main>
    </div>
  );
}
