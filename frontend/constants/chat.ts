/**
 * Constants for chat functionality
 */

// Standard chat suggestions - for backend multi-agent system
// These work with the backend and don't require real-time stock data
export const STANDARD_CHAT_SUGGESTIONS = [
  {
    text: "What is the PDT rule?",
    category: "education" as const,
  },
  {
    text: "How do I get started with trading?",
    category: "education" as const,
  },
  {
    text: "What patterns should I watch in SPY?",
    category: "analysis" as const,
  },
  {
    text: "Short insight (bullish/bearish) in one sentence.",
    category: "analysis" as const,
  },
  {
    text: "What are common trading mistakes?",
    category: "education" as const,
  },
  {
    text: "How to maintain healthy trading habits and avoid compulsive behavior?",
    category: "education" as const,
  },
] as const;

// Compare chat suggestions - for multi-LLM comparison with real-time data
// Organized by category: Market & Analysis (combines stock prices and analysis), Setup/Education
export const COMPARE_CHAT_SUGGESTIONS = [
  // Market & Analysis (combines stock prices and market analysis)
  {
    text: "What's the current price of SPY?",
    category: "market" as const,
  },
  {
    text: "What's the current price of TSLA?",
    category: "market" as const,
  },
  {
    text: "Any headlines, Fed updates, or macro data affecting SPY or TSLA?",
    category: "market" as const,
  },
  {
    text: "What's the options flow or put/call ratio?",
    category: "market" as const,
  },
  {
    text: "Short insight (bullish/bearish) in one sentence for TSLA.",
    category: "market" as const,
  },
  {
    text: "What patterns should I watch in SPY?",
    category: "market" as const,
  },
  {
    text: "Analyze Tesla trading patterns",
    category: "market" as const,
  },
  // Setup & Education
  {
    text: "How to open Robinhood account and documents needed?",
    category: "setup" as const,
  },
  {
    text: "What is the PDT rule?",
    category: "setup" as const,
  },
  {
    text: "How do I get started with trading?",
    category: "setup" as const,
  },
  {
    text: "How to maintain healthy trading habits and avoid compulsive behavior?",
    category: "setup" as const,
  },
] as const;

// Legacy export for backward compatibility (used by compare mode)
export const CHAT_SUGGESTIONS = COMPARE_CHAT_SUGGESTIONS;

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


