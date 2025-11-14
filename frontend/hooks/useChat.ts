/**
 * useChat Hook
 * 
 * Custom hook for managing chat functionality.
 * Separates business logic from UI components for better testability and reusability.
 * 
 * Features:
 * - Message state management
 * - API integration
 * - Error handling
 * - Loading states
 * 
 * Future Enhancements:
 * - Message persistence
 * - Optimistic updates
 * - Retry logic
 * - Message queuing
 */

import { useState, useCallback } from "react";
import { sendChatMessage } from "@/lib/api";
import { Message } from "@/types/chat";

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (content: string) => Promise<void>;
  clearError: () => void;
  clearMessages: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    setError(null);

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const history = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const responseText = await sendChatMessage(content.trim(), history);

      const aiMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: responseText,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      // Format error message for better readability
      let errorContent = err instanceof Error 
        ? err.message 
        : "Sorry, I couldn't connect to the server. Please make sure the backend is running.";
      
      // If it's a network error, provide helpful instructions
      if (errorContent.includes("Backend server is not running")) {
        // Format the multi-line error message
        errorContent = errorContent.replace(/\n\n/g, "\n");
      } else if (errorContent.includes("Network error") || errorContent.includes("Could not connect")) {
        errorContent = `Backend Server Not Running

Standard Chat requires the backend server to be running.

To start the backend:
1. Open terminal
2. Run: cd tradepal-ai/backend
3. Run: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

Alternative: Use Compare Chat (top navigation) which works without the backend and includes real-time stock data and news.`;
      }
      
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: errorContent,
        timestamp: new Date(),
        error: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to connect to backend. Is the server running on port 8000?"
      );
    } finally {
      setIsLoading(false);
    }
  }, [messages, isLoading]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearError,
    clearMessages,
  };
}

