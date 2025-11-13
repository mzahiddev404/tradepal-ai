/**
 * Constants for chat functionality
 */

export const CHAT_SUGGESTIONS = [
  {
    text: "What's the current Tesla stock price?",
    category: "stock" as const,
  },
  {
    text: "What was TSLA's opening price yesterday?",
    category: "stock" as const,
  },
  {
    text: "Analyze sentiment correlation for TSLA and SPY",
    category: "stock" as const,
  },
  {
    text: "What are your pricing plans?",
    category: "billing" as const,
  },
  {
    text: "How do I troubleshoot connection issues?",
    category: "technical" as const,
  },
  {
    text: "What is your privacy policy?",
    category: "policy" as const,
  },
] as const;

export const ERROR_MESSAGES = {
  CONNECTION_FAILED: "Sorry, I couldn't connect to the server. Please make sure the backend is running.",
  GENERIC_ERROR: "An error occurred. Please try again.",
  BACKEND_NOT_RUNNING: "Failed to connect to backend. Is the server running on port 8000?",
} as const;

export const CHAT_CONFIG = {
  MAX_MESSAGE_LENGTH: 1000,
  DEBOUNCE_DELAY: 300,
  AUTO_SCROLL_DELAY: 100,
} as const;

