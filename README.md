# TradePal AI

Stock market trading assistant with multi-agent AI system, real-time market data, and document analysis.

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- OpenAI API key (required for backend)
- Optional: Alpha Vantage API key (falls back to yfinance)

### Installation

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Running

**Start Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000`

## Features

- **Multi-Agent Chat**: Intelligent routing to specialized agents (billing, technical, policy, trading)
- **Stock Market Data**: Real-time quotes, options chains, market overview
- **Document Analysis**: Upload PDFs and ask questions about their content
- **Multi-LLM Comparison**: Compare responses from different AI models side-by-side
- **Market Time**: Live market status with Eastern Time clock

## Multi-LLM Comparison

Compare responses from OpenAI, Anthropic, Google Gemini, and OpenRouter models.

### Setup
1. Go to Settings (gear icon)
2. Add API keys for providers you want to use
3. Keys are encrypted and stored locally in your browser
4. Switch to "Compare" mode in the chat header

### Supported Models

**OpenAI** ($ - $$$)
- GPT-4 Turbo, GPT-4, GPT-3.5 Turbo

**Anthropic** ($$ - $$$$)
- Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Sonnet

**Google Gemini** ($ - $$)
- Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini Pro

**OpenRouter** ($ - $$$$)
- Access to multiple models via single API key

Cost indicators in dropdown: $ = Low, $$ = Medium, $$$ = High, $$$$ = Premium

### Compare Mode vs Standard Mode

**Compare Mode**: Direct API calls from browser. Good for comparing raw model responses. No backend features like stock data or document context.

**Standard Mode**: Full backend access with stock data, document analysis, multi-agent routing, and market sentiment.

## API Keys

Get your keys:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys
- Google Gemini: https://makersuite.google.com/app/apikey
- OpenRouter: https://openrouter.ai/keys

All keys are encrypted using Web Crypto API and stored in browser localStorage. Never sent to TradePal servers.

## Environment Variables

Create `.env` files:

**Backend** (`backend/.env`):
```
OPENAI_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here  # Optional
```

**Frontend** (`frontend/.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
tradepal-ai/
├── backend/          # FastAPI backend
│   ├── api/         # API routes
│   ├── utils/       # Agents and services
│   └── models/      # Data models
├── frontend/        # Next.js frontend
│   ├── app/         # Pages and API routes
│   ├── components/  # React components
│   └── lib/         # Utilities
└── projectspec/     # Project specifications
```

## Tech Stack

**Backend:**
- FastAPI
- LangChain & LangGraph
- ChromaDB (vector storage)
- yfinance, Alpha Vantage (market data)

**Frontend:**
- Next.js 16
- React 18 + TypeScript
- Tailwind CSS
- shadcn/ui
- AI SDK v5

## Documentation

- `SETUP_GUIDE.md` - Detailed setup instructions
- `backend/README.md` - Backend API documentation
- `backend/API_INTEGRATIONS.md` - API integration details
- `backend/CHROMADB_SETUP.md` - ChromaDB configuration
- `frontend/README.md` - Frontend development guide

## License

See LICENSE file for details.
