"use client";

import { Message } from "@/types/chat";
import { MessageItem } from "./message-item";
import { EmptyState } from "@/components/ui/empty-state";
import { Spinner } from "@/components/ui/spinner";
import { cn } from "@/lib/utils";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex h-full items-center justify-center py-12">
        <div className="text-center space-y-5 max-w-md px-4">
          <div className="mx-auto w-20 h-20 rounded-lg bg-gradient-to-br from-[#34c759] to-[#28a745] border-2 border-[#28a745] flex items-center justify-center shadow-xl">
            <svg
              className="w-10 h-10 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2.5}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <div className="space-y-2">
            <p className="text-2xl font-bold text-[#dcdcdc] uppercase tracking-tight">
              Trading Education Center
            </p>
            <p className="text-sm text-[#969696] leading-relaxed">
              Learn trading patterns, analyze SPY & Tesla, understand SEC rules, get started with trading
            </p>
            <div className="pt-2 flex items-center justify-center gap-2">
              <div className="h-1.5 w-1.5 rounded-full bg-[#34c759]"></div>
              <span className="text-xs text-[#6a6a6a] uppercase tracking-wider">SPY • TSLA • Patterns</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 pb-4">
      {messages.map((message, index) => (
        <div
          key={message.id}
          className="animate-in fade-in slide-in-from-bottom-2 duration-300"
          style={{ animationDelay: `${index * 50}ms` }}
        >
          <MessageBubble message={message} />
        </div>
      ))}
      {isLoading && <LoadingIndicator />}
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const timeString = message.timestamp.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      className={cn(
        "flex w-full mb-3",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[85%] sm:max-w-[75%] rounded-md px-4 py-3 border-l-4 transition-all",
          isUser
            ? "bg-gradient-to-r from-[#34c759]/20 to-[#28a745]/10 border-[#34c759] text-[#dcdcdc] shadow-md"
            : message.error
            ? "bg-[#2d1f1f] border-[#ff3b30] text-[#ff6b6b]"
            : "bg-[#23272c] border-[#007aff] text-[#dcdcdc] shadow-sm"
        )}
      >
        {!isUser && (
          <div className="flex items-center gap-2 mb-2">
            <div className="h-2 w-2 rounded-full bg-[#34c759]"></div>
            <span className="text-xs font-semibold text-[#34c759] uppercase tracking-wide">TradePal AI</span>
          </div>
        )}
        <p className="whitespace-pre-wrap break-words leading-relaxed text-sm sm:text-base">
          {message.content}
        </p>
        <p
          className={cn(
            "mt-2 text-xs trading-number opacity-70",
            isUser ? "text-right text-[#969696]" : "text-left text-[#6a6a6a]"
          )}
        >
          {timeString}
        </p>
      </div>
    </div>
  );
}

function LoadingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="rounded-md bg-[#23272c] border-l-4 border-[#34c759] px-4 py-3 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="h-2 w-2 animate-bounce rounded-full bg-[#34c759] [animation-delay:-0.3s]"></div>
            <div className="h-2 w-2 animate-bounce rounded-full bg-[#34c759] [animation-delay:-0.15s]"></div>
            <div className="h-2 w-2 animate-bounce rounded-full bg-[#34c759]"></div>
          </div>
          <span className="text-xs text-[#6a6a6a] ml-2 uppercase tracking-wide">Analyzing...</span>
        </div>
      </div>
    </div>
  );
}

