"use client";

/**
 * Chat Container Component
 * 
 * Main container managing chat interface and document upload views.
 * 
 * Responsibilities:
 * - Message state management via useChat hook
 * - UI switching between chat and upload views
 * - Auto-scroll functionality
 * - Error handling and display
 * 
 * Future Enhancements:
 * - Message persistence across sessions
 * - Export conversation functionality
 * - Message search and filtering
 * - Customizable UI themes
 */

import { useState, useEffect, useRef } from "react";
import { MessageList } from "./message-list";
import { ChatInput } from "./chat-input";
import { ChatHeader } from "./chat-header";
import { UploadView } from "./upload-view";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useChat } from "@/hooks/useChat";
import { CHAT_SUGGESTIONS } from "@/constants/chat";

export function ChatContainer() {
  const [showUpload, setShowUpload] = useState(false);
  const { messages, isLoading, error, sendMessage, clearError } = useChat();
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector(
        '[data-slot="scroll-area-viewport"]'
      );
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  const handleToggleUpload = () => {
    setShowUpload((prev) => !prev);
    clearError();
  };

  const handleReturnToChat = () => {
    setShowUpload(false);
    clearError();
  };

  return (
    <Card className="flex h-[calc(100vh-8rem)] sm:h-[calc(100vh-6rem)] w-full flex-col overflow-hidden shadow-xl border border-slate-200 bg-white">
      <ChatHeader
        showUpload={showUpload}
        onToggleUpload={handleToggleUpload}
        error={error}
      />

      {showUpload ? (
        <UploadView onReturnToChat={handleReturnToChat} />
      ) : (
        <>
          <div ref={scrollAreaRef} className="flex-1 overflow-hidden bg-gradient-to-b from-slate-50 to-white">
            <ScrollArea className="h-full p-4 sm:p-6 lg:p-8">
              <MessageList messages={messages} isLoading={isLoading} />
            </ScrollArea>
          </div>

          <div className="border-t border-slate-200 bg-white p-4 sm:p-6 shadow-sm">
            <ChatInput
              onSend={sendMessage}
              disabled={isLoading}
              suggestions={messages.length === 0 ? CHAT_SUGGESTIONS.map((s) => s.text) : undefined}
            />
          </div>
        </>
      )}
    </Card>
  );
}

