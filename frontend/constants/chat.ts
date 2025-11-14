/**
 * Constants for chat functionality
 */

export const CHAT_SUGGESTIONS = [
  {
    text: "What's the current price of SPY?",
    category: "stock" as const,
  },
  {
    text: "What's the current price of TSLA?",
    category: "stock" as const,
  },
  {
    text: "Where's the next support and resistance?",
    category: "stock" as const,
  },
  {
    text: "Any headlines, Fed updates, or macro data affecting SPY or TSLA?",
    category: "stock" as const,
  },
  {
    text: "What's the options flow or put/call ratio?",
    category: "stock" as const,
  },
  {
    text: "Short insight (bullish/bearish) in one sentence.",
    category: "stock" as const,
  },
  {
    text: "What patterns should I watch in SPY?",
    category: "stock" as const,
  },
  {
    text: "Analyze Tesla trading patterns",
    category: "stock" as const,
  },
  {
    text: "What is the PDT rule?",
    category: "stock" as const,
  },
  {
    text: "How do I get started with trading?",
    category: "stock" as const,
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


