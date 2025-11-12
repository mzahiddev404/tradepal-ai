# Setup Guide

## Prerequisites

- Node.js 18+
- Python 3.9+
- OpenAI API key
- Alpha Vantage API key (optional)

## Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: add OPENAI_API_KEY and ALPHA_VANTAGE_API_KEY
python main.py
```

Backend: http://localhost:8000

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000

## Testing

1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open http://localhost:3000
4. Ask: "What's the current Tesla stock price?"

## Troubleshooting

**Backend errors**: Check `.env` has `OPENAI_API_KEY`  
**No stock data**: Verify `ALPHA_VANTAGE_API_KEY` or yfinance fallback will be used  
**Frontend can't connect**: Ensure backend is running on port 8000
