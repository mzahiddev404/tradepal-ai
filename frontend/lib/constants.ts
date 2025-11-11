/**
 * Application constants and configuration values
 */

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
export const ENDPOINTS = {
  chat: '/api/chat',
  health: '/api/health',
  upload: '/api/upload',
  stock: {
    quote: '/api/stock/quote',
    options: '/api/stock/options',
    overview: '/api/stock/market/overview',
  },
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

