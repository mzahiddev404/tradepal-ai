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
        "flex w-full mb-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[85%] sm:max-w-[70%] rounded-lg px-4 py-2.5",
          isUser
            ? "bg-slate-900 text-white"
            : isError
            ? "bg-red-50 border border-red-200 text-red-900"
            : "bg-white border border-slate-200 text-slate-900 shadow-sm"
        )}
        role={isError ? "alert" : undefined}
      >
        <p className="text-sm sm:text-base whitespace-pre-wrap break-words leading-relaxed">
          {message.content}
        </p>
        <p
          className={cn(
            "text-xs mt-1.5",
            isUser ? "text-slate-400 text-right" : "text-slate-500 text-left"
          )}
        >
          {formatMessageTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
}

