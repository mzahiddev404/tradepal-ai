/**
 * Individual message item component
 * Separated for better reusability and testability
 */
import { Message } from "@/types/chat";
import { formatMessageTime } from "@/lib/format";
import { cn } from "@/lib/utils";

interface MessageItemProps {
  message: Message;
}

export function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === "user";
  const isError = message.error;

  return (
    <div
      className={cn(
        "flex w-full mb-3",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[85%] sm:max-w-[75%] rounded-md px-4 py-3 border-l-4",
          isUser
            ? "bg-gradient-to-r from-[#34c759]/20 to-[#28a745]/10 border-[#34c759] text-[#dcdcdc] shadow-md"
            : isError
            ? "bg-[#2d1f1f] border-[#ff3b30] text-[#ff6b6b]"
            : "bg-[#23272c] border-[#007aff] text-[#dcdcdc] shadow-sm"
        )}
        role={isError ? "alert" : undefined}
      >
        {!isUser && (
          <div className="flex items-center gap-2 mb-2">
            <div className="h-2 w-2 rounded-full bg-[#34c759]"></div>
            <span className="text-xs font-semibold text-[#34c759] uppercase tracking-wide">TradePal AI</span>
          </div>
        )}
        <p className="text-sm sm:text-base whitespace-pre-wrap break-words leading-relaxed">
          {message.content}
        </p>
        <p
          className={cn(
            "text-xs mt-2 trading-number opacity-70",
            isUser ? "text-right text-[#969696]" : "text-left text-[#6a6a6a]"
          )}
        >
          {formatMessageTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
}

