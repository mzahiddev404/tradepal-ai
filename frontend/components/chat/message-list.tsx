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
        <div className="text-center space-y-4 max-w-md px-4">
          <div className="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
            <svg
              className="w-8 h-8 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          </div>
          <div className="space-y-2">
            <p className="text-xl font-bold text-slate-900">
              Start a conversation
            </p>
            <p className="text-sm text-slate-600 leading-relaxed">
              Ask questions about billing, stock prices, technical support, or policies
            </p>
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
        "flex w-full",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[85%] sm:max-w-[70%] rounded-lg px-4 py-3 transition-all",
          isUser
            ? "bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-md"
            : message.error
            ? "bg-red-50 border border-red-200 text-red-900 shadow-sm"
            : "bg-white border border-slate-200 text-slate-900 shadow-md"
        )}
      >
        <p className="whitespace-pre-wrap break-words leading-relaxed text-sm sm:text-base">
          {message.content}
        </p>
        <p
          className={cn(
            "mt-2 text-xs",
            isUser ? "text-right text-blue-100" : "text-left text-slate-500"
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
      <div className="rounded-lg bg-white border border-slate-200 px-4 py-3 shadow-sm">
        <div className="flex gap-1.5 items-center">
          <div className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]"></div>
          <div className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]"></div>
          <div className="h-2 w-2 animate-bounce rounded-full bg-slate-400"></div>
        </div>
      </div>
    </div>
  );
}

