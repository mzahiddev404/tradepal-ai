"use client";

/**
 * Compare Page
 * 
 * Dedicated page for multi-LLM comparison feature.
 * Provides a full-screen comparison view.
 */

import { MultiLLMComparison } from "@/components/chat/multi-llm-comparison";
import { ErrorBoundary } from "@/components/error-boundary";
import { AppHeader } from "@/components/layout/app-header";
import { useState } from "react";
import { useRouter } from "next/navigation";

type ChatMode = "standard" | "multi-llm";

export default function ComparePage() {
  const router = useRouter();
  const [chatMode, setChatMode] = useState<ChatMode>("multi-llm");
  const [showUpload, setShowUpload] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleModeChange = (mode: ChatMode) => {
    if (mode === "standard") {
      // Navigate to home page
      router.push("/");
    } else {
      // Already on compare page, just update state
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
              <div className="h-full border border-[#2d3237]/50 bg-[#1a1e23]/95 backdrop-blur-sm shadow-2xl rounded-lg overflow-hidden">
                <MultiLLMComparison />
              </div>
            </ErrorBoundary>
          </div>
        </div>
      </div>
    </div>
  );
}

