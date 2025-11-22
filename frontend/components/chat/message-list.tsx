"use client";

import { Message } from "@/types/chat";
import { MessageItem } from "./message-item";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  if (messages.length === 0 && !isLoading) {
    return <TerminalWelcome />;
  }

  return (
    <div className="flex flex-col gap-2 pb-4">
      {messages.map((message, index) => (
        <div
          key={message.id}
          className="animate-in fade-in slide-in-from-bottom-2 duration-300"
          style={{ animationDelay: `${index * 50}ms` }}
        >
          <MessageItem message={message} />
        </div>
      ))}
      {isLoading && <LoadingIndicator />}
    </div>
  );
}

function TerminalWelcome() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="flex h-full items-center justify-center py-12 opacity-0 animate-in fade-in duration-1000 fill-mode-forwards">
      <div className="max-w-lg w-full bg-[#0F1115]/80 border border-[#34c759]/20 rounded-sm p-6 font-mono text-sm relative overflow-hidden shadow-[0_0_30px_rgba(52,199,89,0.05)]">
        {/* Scanline */}
        <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(to_bottom,rgba(52,199,89,0.03)_1px,transparent_1px)] bg-[size:100%_2px]"></div>
        
        <div className="space-y-2 text-gray-400">
          <div className="flex justify-between border-b border-gray-800 pb-2 mb-4">
            <span className="text-[#34c759]">TRADEPAL_TERMINAL_v2.0</span>
            <span>{mounted ? "ONLINE" : "BOOTING..."}</span>
          </div>
          
          <div className="space-y-1">
            <p className="flex gap-2">
              <span className="text-gray-600">00:00:01</span>
              <span className="text-blue-400">INFO</span>
              <span>Initializing quantum interface...</span>
            </p>
            <p className="flex gap-2">
              <span className="text-gray-600">00:00:02</span>
              <span className="text-blue-400">INFO</span>
              <span>Connecting to market data streams... [SPY, TSLA]</span>
            </p>
            <p className="flex gap-2">
              <span className="text-gray-600">00:00:03</span>
              <span className="text-blue-400">INFO</span>
              <span>Loading neural weights...</span>
            </p>
            <p className="flex gap-2">
              <span className="text-gray-600">00:00:04</span>
              <span className="text-[#34c759]">SUCCESS</span>
              <span>System ready. Awaiting command.</span>
            </p>
          </div>

          <div className="mt-6 pt-4 border-t border-gray-800">
            <p className="text-xs text-gray-500 uppercase tracking-widest mb-2">Available Modules</p>
            <div className="grid grid-cols-2 gap-2">
              <div className="flex items-center gap-2 bg-white/5 p-2 rounded border border-white/5">
                <div className="h-1.5 w-1.5 rounded-full bg-[#34c759]"></div>
                <span>Market Analysis</span>
              </div>
              <div className="flex items-center gap-2 bg-white/5 p-2 rounded border border-white/5">
                <div className="h-1.5 w-1.5 rounded-full bg-[#34c759]"></div>
                <span>Pattern Recognition</span>
              </div>
              <div className="flex items-center gap-2 bg-white/5 p-2 rounded border border-white/5">
                <div className="h-1.5 w-1.5 rounded-full bg-[#34c759]"></div>
                <span>Risk Assessment</span>
              </div>
              <div className="flex items-center gap-2 bg-white/5 p-2 rounded border border-white/5">
                <div className="h-1.5 w-1.5 rounded-full bg-[#34c759]"></div>
                <span>Multi-Model Compare</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LoadingIndicator() {
  return (
    <div className="flex w-full mb-4 animate-in fade-in slide-in-from-bottom-2">
      <div className="max-w-[80%] pl-4 pr-4 py-2 border-l-2 border-[#34c759] bg-[rgba(52,199,89,0.05)]">
        <div className="flex items-center gap-2 mb-1 opacity-80">
          <span className="text-[10px] font-mono font-semibold text-[#34c759] uppercase tracking-wider">
            PROCESSING
          </span>
        </div>
        <div className="flex items-center gap-1 h-6">
          <span className="h-1.5 w-1.5 bg-[#34c759] rounded-sm animate-pulse"></span>
          <span className="h-1.5 w-1.5 bg-[#34c759] rounded-sm animate-pulse delay-75"></span>
          <span className="h-1.5 w-1.5 bg-[#34c759] rounded-sm animate-pulse delay-150"></span>
          <span className="ml-2 font-mono text-xs text-[#34c759] animate-pulse">Analyzing market data...</span>
        </div>
      </div>
    </div>
  );
}
