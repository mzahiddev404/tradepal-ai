# Backend API

FastAPI backend with stock data and AI chat capabilities.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add OPENAI_API_KEY and ALPHA_VANTAGE_API_KEY to .env
python main.py
```

## Endpoints

**Chat**
- `POST /api/chat` - Send message to AI agent

**Stock Data**
- `GET /api/stock/quote/{symbol}` - Current quote
- `GET /api/stock/quote/{symbol}?include_sentiment=true` - Quote with sentiment
- `GET /api/stock/historical/{symbol}?date=YYYY-MM-DD` - Historical price
- `GET /api/stock/options/{symbol}` - Options chain
- `GET /api/stock/market/overview` - Market indices

**Health**
- `GET /api/health` - Health check

## Services

- `stock_data_service` - Alpha Vantage + yfinance integration
- `sentiment_analyzer` - News + Reddit sentiment analysis
- `chat_agent` - LangChain agent with stock query detection

## Configuration

See `core/config.py` for settings. Loads from `.env`:
- `OPENAI_API_KEY` (required)
- `ALPHA_VANTAGE_API_KEY` (optional)
