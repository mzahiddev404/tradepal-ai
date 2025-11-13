/**
 * Application constants and configuration values
 */

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Color palette
export const COLORS = {
  primary: {
    main: 'teal',
    light: 'cyan',
    dark: 'emerald',
  },
  accent: {
    main: 'amber',
    light: 'yellow',
  },
  semantic: {
    success: 'green',
    error: 'red',
    warning: 'amber',
    info: 'blue',
  },
} as const;

// Application metadata
export const APP_CONFIG = {
  name: 'TradePal AI',
  version: '1.0.0',
  description: 'Professional AI-powered trading assistant',
  features: [
    'Real-time stock market data',
    'Intelligent chat assistance',
    'Options chain analysis',
    'Market overview dashboard',
  ],
} as const;

// API endpoints
export const API_ENDPOINTS = {
  CHAT: "/api/chat",
  HEALTH: "/api/health",
  UPLOAD: "/api/upload",
  STOCK_QUOTE: "/api/stock/quote",
  STOCK_QUOTES: "/api/stock/quotes",
  MARKET_OVERVIEW: "/api/stock/market/overview",
  OPTIONS: "/api/stock/options",
  HISTORICAL: "/api/stock/historical",
  SENTIMENT_CORRELATION: "/api/sentiment/correlation",
} as const;

// UI constants
export const UI_CONFIG = {
  animation: {
    duration: 300,
    easing: 'ease-out',
  },
  breakpoints: {
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
  },
} as const;

