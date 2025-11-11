"use client";

import { useState, useRef, useEffect } from "react";
import { MessageList } from "./message-list";
import { ChatInput } from "./chat-input";
import { PDFUpload } from "./pdf-upload";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { FileText, TrendingUp, AlertTriangle } from "lucide-react";
import Link from "next/link";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  error?: boolean;
}

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Clear any previous errors
    setError(null);

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Import API client dynamically
      const { sendChatMessage } = await import("@/lib/api");
      
      // Prepare history for API (only role and content)
      const history = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      // Get response from backend
      const responseText = await sendChatMessage(content.trim(), history);
      
      const aiMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: responseText,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: "Sorry, I couldn't connect to the server. Please make sure the backend is running.",
        timestamp: new Date(),
        error: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
      setError("Failed to connect to backend. Is the server running on port 8000?");
      console.error("Chat error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="flex h-[calc(100vh-4rem)] w-full flex-col overflow-hidden shadow-2xl border-2 border-teal-200 backdrop-blur-md bg-white/90">
      <div className="border-b-2 border-teal-100 bg-gradient-to-r from-teal-600 via-cyan-600 to-emerald-600 p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/20 backdrop-blur-sm">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white drop-shadow-lg">
                TradePal AI Assistant
              </h1>
            </div>
            <p className="text-sm text-teal-100">
              Ask me anything about billing, stock prices, technical support, or policies
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link href="/market">
              <Button 
                variant="outline" 
                size="sm" 
                className="transition-all hover:scale-105 hover:shadow-lg active:scale-95 bg-white/90 hover:bg-white border-teal-200 hover:border-teal-300"
              >
                <TrendingUp className="mr-2 h-4 w-4 text-green-600" />
                <span className="text-teal-900">Market</span>
              </Button>
            </Link>
            <Link href="/disclaimer">
              <Button 
                variant="outline" 
                size="sm" 
                className="transition-all hover:scale-105 hover:shadow-lg active:scale-95 bg-white/90 hover:bg-white border-teal-200 hover:border-teal-300"
              >
                <AlertTriangle className="mr-2 h-4 w-4 text-amber-600" />
                <span className="text-teal-900">Disclaimer</span>
              </Button>
            </Link>
            <Button
              variant={showUpload ? "default" : "outline"}
              size="sm"
              onClick={() => setShowUpload(!showUpload)}
              className={showUpload 
                ? "transition-all hover:scale-105 hover:shadow-lg active:scale-95 bg-teal-600 hover:bg-teal-700 text-white" 
                : "transition-all hover:scale-105 hover:shadow-lg active:scale-95 bg-white/90 hover:bg-white border-teal-200 hover:border-teal-300 text-teal-900"
              }
            >
              <FileText className="mr-2 h-4 w-4" />
              Documents
            </Button>
          </div>
        </div>
        {error && (
          <div className="mt-3 rounded-lg bg-red-100 border-2 border-red-300 p-3 text-sm text-red-800 animate-in fade-in slide-in-from-top-2 shadow-lg">
            {error}
          </div>
        )}
      </div>

      {showUpload ? (
        <ScrollArea className="flex-1 p-4 sm:p-6" ref={scrollAreaRef}>
          <PDFUpload
            onUploadComplete={(files) => {
              console.log("Files uploaded:", files);
              // Will connect to backend in Step 4
            }}
          />
        </ScrollArea>
      ) : (
        <>
          <ScrollArea className="flex-1 p-4 sm:p-6" ref={scrollAreaRef}>
            <MessageList messages={messages} isLoading={isLoading} />
          </ScrollArea>

          <div className="border-t-2 border-teal-100 bg-gradient-to-t from-teal-50 via-cyan-50 to-transparent p-4 sm:p-6">
            <ChatInput onSend={handleSendMessage} disabled={isLoading} />
          </div>
        </>
      )}
    </Card>
  );
}

