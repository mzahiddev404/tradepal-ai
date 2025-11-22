"use client";

/**
 * Chat Container Component
 * 
 * Main container managing chat interface and document upload views.
 * 
 * Responsibilities:
 * - Message state management via useChat hook
 * - UI switching between chat and upload views
 * - Mode switching between Standard Chat and Multi-LLM Compare
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
import { UploadView } from "./upload-view";
import { MultiLLMComparison } from "./multi-llm-comparison";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useChat } from "@/hooks/useChat";
import { STANDARD_CHAT_SUGGESTIONS } from "@/constants/chat";

type ChatMode = "standard" | "multi-llm";

interface ChatContainerProps {
  chatMode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  showUpload: boolean;
  onToggleUpload: () => void;
  onError?: (error: string | null) => void;
}

export function ChatContainer({
  chatMode,
  onModeChange,
  showUpload,
  onToggleUpload,
  onError,
}: ChatContainerProps) {
  const { messages, isLoading, error, sendMessage, clearError } = useChat();
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (error && onError) {
      onError(error);
    } else if (onError) {
      onError(null);
    }
  }, [error, onError]);

  useEffect(() => {
    if (scrollAreaRef.current && chatMode === "standard") {
      const scrollContainer = scrollAreaRef.current.querySelector(
        '[data-slot="scroll-area-viewport"]'
      );
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages, chatMode]);

  const handleReturnToChat = () => {
    onToggleUpload();
    clearError();
  };

  return (
    <Card className="flex h-full w-full flex-col overflow-hidden trading-panel">
      {showUpload ? (
        <UploadView onReturnToChat={handleReturnToChat} />
      ) : chatMode === "multi-llm" ? (
        <MultiLLMComparison />
      ) : (
        <>
          <div ref={scrollAreaRef} className="flex-1 overflow-hidden bg-transparent">
            <ScrollArea className="h-full p-4 sm:p-6 lg:p-8">
              <MessageList messages={messages} isLoading={isLoading} />
            </ScrollArea>
          </div>

          <div className="border-t border-white/5 bg-black/20 p-4 sm:p-6 backdrop-blur-md">
            <ChatInput
              onSend={sendMessage}
              disabled={isLoading}
              suggestions={STANDARD_CHAT_SUGGESTIONS.map((s) => s.text)}
            />
          </div>
        </>
      )}
    </Card>
  );
}
