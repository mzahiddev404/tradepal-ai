"use client";

import { AppSidebar } from "@/components/layout/app-sidebar";
import { RightSidebar } from "@/components/layout/right-sidebar";
import { ChatContainer } from "@/components/chat/chat-container";
import { ErrorBoundary } from "@/components/error-boundary";
import { MarketTime } from "@/components/chat/market-time";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";

type ChatMode = "standard" | "multi-llm";

export default function Home() {
  const router = useRouter();
  const [chatMode, setChatMode] = useState<ChatMode>("standard");
  const [showUpload, setShowUpload] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleModeChange = (mode: ChatMode) => {
    if (mode === "multi-llm") {
      // Navigate to compare page or just switch mode? 
      // Previous implementation linked to /compare, but sidebar handles state.
      // Let's support both. If we stay on Home, we show compare.
      setChatMode(mode);
    } else {
      setChatMode(mode);
      setShowUpload(false);
      setError(null);
    }
  };

  const handleToggleUpload = () => {
    setShowUpload((prev) => !prev);
    setError(null);
  };

  return (
    <div className="flex h-screen w-full bg-[#0F1115] bg-grid-subtle text-[#dcdcdc] overflow-hidden">
      {/* Left Sidebar - Navigation */}
      <AppSidebar 
        chatMode={chatMode} 
        onModeChange={handleModeChange}
        showDocuments={showUpload}
        onToggleDocuments={handleToggleUpload}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0">
        
        {/* Header - Desktop & Mobile */}
        <header className="h-14 border-b border-white/5 flex items-center justify-between px-4 sm:px-6 bg-[#131619]/50 backdrop-blur-sm shrink-0 z-10">
          
          {/* Mobile Menu / Brand (Simplified for Mobile) */}
          <div className="flex items-center gap-3 md:hidden">
             <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-gradient-to-br from-[#34c759] to-[#28a745]">
               <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
               </svg>
             </div>
             <span className="font-bold text-white tracking-tight">TRADEPAL</span>
          </div>

          {/* Desktop Breadcrumb / Title */}
          <div className="hidden md:flex items-center text-sm font-medium text-gray-400">
             <span className="text-gray-500">Workspace</span>
             <span className="mx-2">/</span>
             <span className="text-white">
               {chatMode === "standard" && !showUpload ? "Standard Chat" : 
                chatMode === "multi-llm" ? "Model Comparison" : 
                "Knowledge Base"}
             </span>
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-4">
            <MarketTime />
          </div>
        </header>

        {/* Content Container */}
        <div className="flex-1 relative overflow-hidden p-4 sm:p-6">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg mb-4 text-sm flex items-center gap-2 animate-in fade-in slide-in-from-top-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
              {error}
            </div>
          )}
          
          <ErrorBoundary>
            <ChatContainer
              chatMode={chatMode}
              onModeChange={handleModeChange}
              showUpload={showUpload}
              onToggleUpload={handleToggleUpload}
              onError={setError}
            />
          </ErrorBoundary>
        </div>
      </main>

      {/* Right Sidebar - Market Intelligence */}
      <RightSidebar />
    </div>
  );
}
