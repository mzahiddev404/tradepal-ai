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
        "flex w-full mb-4 animate-in fade-in slide-in-from-bottom-2",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div
        className={cn(
          "max-w-[85%] sm:max-w-[80%] pl-4 pr-4 py-2 relative",
          isUser
            ? "border-r-2 border-[#34c759] bg-[rgba(52,199,89,0.05)] text-right"
            : isError
            ? "border-l-2 border-[#ff3b30] bg-[rgba(255,59,48,0.05)]"
            : "border-l-2 border-[#007aff] bg-[rgba(0,122,255,0.05)]"
        )}
        role={isError ? "alert" : undefined}
      >
        {!isUser && (
          <div className="flex items-center gap-2 mb-1 opacity-80">
            <span className="text-[10px] font-mono font-semibold text-[#007aff] uppercase tracking-wider">
              SYSTEM_RESPONSE
            </span>
          </div>
        )}
        {isUser && (
          <div className="flex items-center justify-end gap-2 mb-1 opacity-80">
            <span className="text-[10px] font-mono font-semibold text-[#34c759] uppercase tracking-wider">
              USER_INPUT
            </span>
          </div>
        )}
        
        <div className={cn(
          "text-sm leading-relaxed whitespace-pre-wrap break-words",
          isUser ? "text-gray-200" : "text-gray-300"
        )}>
          {message.content}
        </div>
        
        <p
          className={cn(
            "text-[10px] mt-2 font-mono opacity-50",
            isUser ? "text-[#34c759]" : "text-[#007aff]"
          )}
        >
          T+{formatMessageTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
}
