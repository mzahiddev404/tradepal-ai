"use client";

import { ChatContainer } from "@/components/chat/chat-container";
import { ErrorBoundary } from "@/components/error-boundary";
import { AppHeader } from "@/components/layout/app-header";
import { useState } from "react";
import { useRouter } from "next/navigation";

type ChatMode = "standard" | "multi-llm";

export default function Home() {
  const router = useRouter();
  const [chatMode, setChatMode] = useState<ChatMode>("standard");
  const [showUpload, setShowUpload] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleModeChange = (mode: ChatMode) => {
    if (mode === "multi-llm") {
      // Navigate to compare page
      router.push("/compare");
    } else {
      // Already on standard page, just update state
      setChatMode(mode);
      setShowUpload(false);
      setError(null);
    }
  };

  const handleToggleUpload = () => {
    setShowUpload((prev) => !prev);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1e23] via-[#23272c] to-[#1a1e23]">
      <AppHeader
        chatMode={chatMode}
        onModeChange={handleModeChange}
        showDocuments={showUpload}
        onToggleDocuments={handleToggleUpload}
        error={error}
      />
      <div className="p-4 sm:p-6 md:p-8">
        <div className="max-w-7xl mx-auto h-[calc(100vh-8rem)] flex items-center justify-center">
          <div className="w-full h-full max-h-[900px]">
            <ErrorBoundary>
              <ChatContainer
                chatMode={chatMode}
                onModeChange={handleModeChange}
                showUpload={showUpload}
                onToggleUpload={handleToggleUpload}
                onError={setError}
              />
            </ErrorBoundary>
          </div>
        </div>
      </div>
    </div>
  );
}
