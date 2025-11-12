# TradePal AI

AI-powered trading assistant with real-time stock data, sentiment analysis, and chat capabilities.

## Quick Start

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add OPENAI_API_KEY and ALPHA_VANTAGE_API_KEY
python main.py
```
API: http://localhost:8000

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:3000

## Features

- Real-time stock quotes (Alpha Vantage primary, yfinance fallback)
- Historical stock prices
- Sentiment analysis (Alpha Vantage News + Reddit WallStreetBets)
- Investment guidance (Call/Put recommendations)
- AI chat agent with stock query detection
- PDF document processing

## Tech Stack

**Frontend**: Next.js 15, TypeScript, Tailwind CSS  
**Backend**: FastAPI, LangChain, OpenAI  
**Data**: Alpha Vantage API, yfinance, Reddit API

## API Endpoints

- `POST /api/chat` - Chat with AI agent
- `GET /api/stock/quote/{symbol}` - Stock quote (optional `?include_sentiment=true`)
- `GET /api/stock/historical/{symbol}?date=YYYY-MM-DD` - Historical price
- `GET /api/stock/options/{symbol}` - Options chain
- `GET /api/stock/market/overview` - Market overview

## Environment Variables

Required in `backend/.env`:
- `OPENAI_API_KEY` - OpenAI API key
- `ALPHA_VANTAGE_API_KEY` - Alpha Vantage API key (optional, falls back to yfinance)

## Project Structure

```
tradepal-ai/
├── frontend/          # Next.js app
├── backend/           # FastAPI server
│   ├── api/          # API routes
│   ├── utils/        # Services (stock_data, sentiment_analysis, langchain_agent)
│   └── models/       # Pydantic models
└── README.md
```

## Status

✅ Production-ready | All integrations working
