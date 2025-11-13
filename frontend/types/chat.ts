/**
 * Type definitions for chat functionality
 */

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  error?: boolean;
}

export interface ChatHistory {
  role: string;
  content: string;
}

export interface ChatSuggestion {
  text: string;
  category?: "stock" | "billing" | "technical" | "policy" | "general";
}

