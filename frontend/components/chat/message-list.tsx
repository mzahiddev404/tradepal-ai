"use client";

import { Message } from "./chat-container";
import { cn } from "@/lib/utils";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center space-y-3 animate-in fade-in duration-500">
          <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
            <svg
              className="w-8 h-8 text-primary"
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
          <p className="text-xl font-semibold text-foreground">
            Start a conversation
          </p>
          <p className="text-sm text-muted-foreground max-w-sm">
            Send a message to get started with TradePal AI
          </p>
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
          "max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 shadow-lg transition-all",
          isUser
            ? "bg-gradient-to-br from-teal-600 via-cyan-600 to-emerald-600 text-white rounded-br-sm shadow-teal-300"
            : message.error
            ? "bg-red-100 border-2 border-red-300 text-red-800 rounded-bl-sm"
            : "bg-white border-2 border-teal-200 text-gray-800 rounded-bl-sm"
        )}
      >
        <p className="whitespace-pre-wrap break-words leading-relaxed">{message.content}</p>
        <p
          className={cn(
            "mt-2 text-xs opacity-60",
            isUser ? "text-right" : "text-left"
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
    <div className="flex justify-start animate-in fade-in">
      <div className="rounded-2xl rounded-bl-sm bg-white border-2 border-teal-200 px-4 py-3 shadow-lg">
        <div className="flex gap-1.5 items-center">
          <div className="h-3 w-3 animate-bounce rounded-full bg-teal-600 [animation-delay:-0.3s]"></div>
          <div className="h-3 w-3 animate-bounce rounded-full bg-cyan-600 [animation-delay:-0.15s]"></div>
          <div className="h-3 w-3 animate-bounce rounded-full bg-emerald-600"></div>
        </div>
      </div>
    </div>
  );
}

