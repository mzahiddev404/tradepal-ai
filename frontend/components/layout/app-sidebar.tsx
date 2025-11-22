"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { 
  TrendingUp, 
  MessageSquare, 
  Settings, 
  AlertTriangle, 
  FileText, 
  GitCompare,
  LayoutDashboard,
  Wifi
} from "lucide-react";

type ChatMode = "standard" | "multi-llm";

interface AppSidebarProps {
  chatMode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  showDocuments: boolean;
  onToggleDocuments: () => void;
}

export function AppSidebar({
  chatMode,
  onModeChange,
  showDocuments,
  onToggleDocuments,
}: AppSidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const isChatPage = pathname === "/" || pathname === "/compare";

  const handleStandardClick = () => {
    if (pathname !== "/") {
      router.push("/");
    }
    if (chatMode !== "standard") {
      onModeChange("standard");
    }
  };

  const handleCompareClick = () => {
    // If we're on a non-chat page, or just want to ensure we're in compare mode
    if (pathname !== "/") {
      router.push("/");
    }
    onModeChange("multi-llm");
  };

  const handleDocumentsClick = () => {
    if (!isChatPage) {
      router.push("/");
      // We might need a way to trigger open after nav, but for now simple nav is fine
      // The user can click again to open. 
      // Ideally we'd use a query param or global state, but let's keep it simple.
    } else {
      onToggleDocuments();
    }
  };

  return (
    <aside className="hidden md:flex flex-col w-64 h-full glass-panel border-r border-white/5 bg-[#131619]/80 backdrop-blur-xl relative overflow-hidden">
      {/* Scanline Effect Overlay */}
      <div className="absolute inset-0 scanlines opacity-5 pointer-events-none z-0"></div>

      {/* Logo Area */}
      <div className="relative z-10 flex flex-col items-center justify-center py-8 border-b border-white/5">
        <div className="relative group cursor-default">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#34c759] to-[#28a745] rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
          <div className="relative flex items-center justify-center h-14 w-14 rounded-xl bg-gradient-to-br from-[#1a1e23] to-[#0f1115] border border-[#34c759]/30 shadow-xl">
            <svg
              className="h-8 w-8 text-[#34c759] drop-shadow-[0_0_8px_rgba(52,199,89,0.5)]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
        </div>
        <h1 className="mt-4 text-xl font-bold text-white tracking-tight glow-text">TRADEPAL</h1>
        <div className="flex items-center gap-1.5 mt-1 px-2 py-0.5 rounded-full bg-white/5 border border-white/5">
          <div className="w-1 h-1 rounded-full bg-[#34c759] animate-pulse"></div>
          <p className="text-[9px] text-gray-400 font-mono tracking-widest uppercase">QUANT TERMINAL</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 flex-1 px-3 py-6 space-y-8 overflow-y-auto custom-scrollbar">
        {/* Main Section */}
        <div className="space-y-1">
          <p className="px-3 text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3 pl-4 border-l border-transparent">Workspace</p>
          
          <Button
            variant="ghost"
            onClick={handleStandardClick}
            className={cn(
              "w-full justify-start gap-3 h-10 transition-all duration-200 relative overflow-hidden group",
              pathname === "/" && chatMode === "standard"
                ? "bg-white/5 text-[#34c759] border-l-2 border-[#34c759] shadow-[inset_10px_0_20px_-10px_rgba(52,199,89,0.1)]" 
                : "text-gray-400 hover:text-white hover:bg-white/5 border-l-2 border-transparent"
            )}
          >
            <MessageSquare className="h-4 w-4 relative z-10" />
            <span className="relative z-10">Standard Chat</span>
            {pathname === "/" && chatMode === "standard" && (
              <div className="absolute inset-0 bg-gradient-to-r from-[#34c759]/10 to-transparent opacity-20"></div>
            )}
          </Button>

          <Button
            variant="ghost"
            onClick={handleCompareClick}
            className={cn(
              "w-full justify-start gap-3 h-10 transition-all duration-200 relative overflow-hidden",
              (pathname === "/compare" || (pathname === "/" && chatMode === "multi-llm"))
                ? "bg-white/5 text-[#34c759] border-l-2 border-[#34c759] shadow-[inset_10px_0_20px_-10px_rgba(52,199,89,0.1)]" 
                : "text-gray-400 hover:text-white hover:bg-white/5 border-l-2 border-transparent"
            )}
          >
            <GitCompare className="h-4 w-4 relative z-10" />
            <span className="relative z-10">Compare Models</span>
          </Button>

          <Button
            variant="ghost"
            onClick={handleDocumentsClick}
            className={cn(
              "w-full justify-start gap-3 h-10 transition-all duration-200 relative overflow-hidden",
              showDocuments
                ? "bg-white/5 text-[#007aff] border-l-2 border-[#007aff] shadow-[inset_10px_0_20px_-10px_rgba(0,122,255,0.1)]" 
                : "text-gray-400 hover:text-white hover:bg-white/5 border-l-2 border-transparent"
            )}
          >
            <FileText className="h-4 w-4 relative z-10" />
            <span className="relative z-10">Knowledge Base</span>
          </Button>
        </div>

        {/* Market Data Section */}
        <div className="space-y-1">
          <p className="px-3 text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3 pl-4 border-l border-transparent">Market Data</p>
          <Link href="/market" className="block w-full">
            <Button
              variant="ghost"
              className={cn(
                "w-full justify-start gap-3 h-10 transition-all duration-200 relative overflow-hidden",
                pathname === "/market"
                  ? "bg-white/5 text-[#34c759] border-l-2 border-[#34c759] shadow-[inset_10px_0_20px_-10px_rgba(52,199,89,0.1)]" 
                  : "text-gray-400 hover:text-white hover:bg-white/5 border-l-2 border-transparent"
              )}
            >
              <TrendingUp className="h-4 w-4 relative z-10" />
              <span className="relative z-10">Live Markets</span>
            </Button>
          </Link>
        </div>

        {/* System Section */}
        <div className="space-y-1">
          <p className="px-3 text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3 pl-4 border-l border-transparent">System</p>
          <Link href="/settings" className="block w-full">
            <Button
              variant="ghost"
              className={cn(
                "w-full justify-start gap-3 h-10 transition-all duration-200 relative overflow-hidden",
                pathname === "/settings"
                  ? "bg-white/5 text-[#34c759] border-l-2 border-[#34c759] shadow-[inset_10px_0_20px_-10px_rgba(52,199,89,0.1)]" 
                  : "text-gray-400 hover:text-white hover:bg-white/5 border-l-2 border-transparent"
              )}
            >
              <Settings className="h-4 w-4 relative z-10" />
              <span className="relative z-10">Settings</span>
            </Button>
          </Link>
          
          <Link href="/disclaimer" className="block w-full">
            <Button
              variant="ghost"
              className={cn(
                "w-full justify-start gap-3 h-10 transition-all duration-200 relative overflow-hidden",
                pathname === "/disclaimer"
                  ? "bg-white/5 text-[#ff9500] border-l-2 border-[#ff9500] shadow-[inset_10px_0_20px_-10px_rgba(255,149,0,0.1)]" 
                  : "text-gray-400 hover:text-white hover:bg-white/5 border-l-2 border-transparent"
              )}
            >
              <AlertTriangle className="h-4 w-4 relative z-10" />
              <span className="relative z-10">Disclaimer</span>
            </Button>
          </Link>
        </div>
      </nav>

      {/* Footer / Status */}
      <div className="relative z-10 p-4 border-t border-white/5 bg-black/20 backdrop-blur-md">
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-2.5">
            <div className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#34c759] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#34c759]"></span>
            </div>
            <span className="text-[10px] text-[#34c759] font-mono tracking-wider">SYSTEM ONLINE</span>
          </div>
          <Wifi className="h-3 w-3 text-gray-600" />
        </div>
      </div>
    </aside>
  );
}
