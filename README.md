# TradePal AI

Advanced customer service AI system powered by a multi-agent architecture with RAG (Retrieval-Augmented Generation) and CAG (Cached-Augmented Generation) capabilities.

## Overview

TradePal AI is a production-ready customer service platform that uses specialized AI agents to handle different types of queries. The system routes questions to appropriate agents (billing, technical support, policy compliance) and retrieves relevant information from uploaded documents using vector search.

## Features

### Core Capabilities
- Multi-agent routing system with intelligent query classification
- Document processing and vector storage (ChromaDB)
- RAG and CAG retrieval strategies for optimal performance
- Real-time stock market data integration
- Sentiment analysis and correlation
- Streaming chat responses
- PDF document upload and processing
- **Multi-LLM Comparison**: Compare responses from multiple LLM providers side-by-side (OpenAI, Anthropic, Google Gemini, OpenRouter)

### Agent Types
- **Orchestrator Agent**: Routes queries to specialized agents using AWS Bedrock
- **Billing Agent**: Hybrid RAG/CAG for pricing and subscription questions
- **Technical Agent**: Pure RAG for dynamic technical documentation
- **Policy Agent**: Pure CAG for static policy documents
- **General Agent**: Handles stock queries and general conversation

## Tech Stack

### Frontend
- Next.js 16 with App Router
- React 18 with TypeScript
- Tailwind CSS for styling
- shadcn/ui component library
- AI SDK v5 for unified LLM provider integration

### Backend
- FastAPI for REST API
- Python 3.13
- LangChain and LangGraph for agent orchestration
- ChromaDB for vector storage
- OpenAI GPT-4/3.5 for LLM
- AWS Bedrock (optional) for cost-effective routing

### Data Sources
- Alpha Vantage API for stock data
- yfinance as fallback for market data
- Reddit API for sentiment analysis

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- OpenAI API key (required for backend)
- Alpha Vantage API key (optional, falls back to yfinance)
- **For Multi-LLM Comparison**: API keys for OpenAI, Anthropic, Google Gemini, or OpenRouter (configured in Settings)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=your_key_here
# ALPHA_VANTAGE_API_KEY=your_key_here (optional)

# Run the server
python main.py
```

Backend will start on `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will start on `http://localhost:3000`

## Project Structure

```
tradepal-ai/
├── backend/
│   ├── api/              # API route handlers
│   │   ├── chat.py      # Chat endpoints
│   │   ├── stock.py      # Stock data endpoints
│   │   ├── upload.py     # File upload endpoints
│   │   └── sentiment_analysis.py
│   ├── core/             # Core configuration
│   │   └── config.py    # Settings management
│   ├── models/           # Pydantic models
│   ├── utils/            # Business logic
│   │   ├── orchestrator.py      # Query routing
│   │   ├── billing_agent.py     # Billing agent
│   │   ├── technical_agent.py   # Technical agent
│   │   ├── policy_agent.py      # Policy agent
│   │   ├── langchain_agent.py   # General agent
│   │   ├── multi_agent_system.py # LangGraph workflow
│   │   ├── chromadb_client.py   # Vector DB client
│   │   └── stock_data.py        # Stock data service
│   ├── tests/            # Test suite
│   └── main.py          # FastAPI app entry point
├── frontend/
│   ├── app/             # Next.js app directory
│   ├── components/      # React components
│   │   ├── chat/        # Chat components
│   │   ├── stock/       # Stock components
│   │   └── ui/          # UI components
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utilities and API clients
│   └── types/           # TypeScript type definitions
└── docs/                # Documentation files
```

## API Endpoints

### Chat
- `POST /api/chat` - Send message to AI agent
- `POST /api/chat/stream` - Streaming chat responses
- `GET /api/health` - Health check

### Stock Data
- `GET /api/stock/quote/{symbol}` - Get stock quote
- `GET /api/stock/quotes?symbols=...` - Multiple quotes
- `GET /api/stock/historical/{symbol}?date=...` - Historical price
- `GET /api/stock/historical/{symbol}/range` - Price range
- `GET /api/stock/options/{symbol}` - Options chain
- `GET /api/stock/market/overview` - Market overview
- `GET /api/stock/event-study/{symbol}` - Event study analysis around religious holidays

### Document Upload
- `POST /api/upload` - Upload PDF documents
- `GET /api/collection/info` - Collection information

### Sentiment Analysis
- `GET /api/sentiment/correlation/{symbol}` - Sentiment correlation
- `GET /api/sentiment/correlation/compare` - Compare sentiment

## Environment Variables

### Backend (.env)
```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Multi-LLM Comparison Feature

TradePal AI includes an optional multi-LLM comparison feature that allows you to compare responses from multiple LLM providers side-by-side. This feature works independently of the backend multi-agent system and runs entirely in the browser.

### Setup

1. **Configure API Keys**: Navigate to Settings (gear icon in the header) or visit `/settings`
2. **Add Provider Keys**: Enter API keys for any of the supported providers:
   - OpenAI (GPT-4, GPT-3.5)
   - Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
   - Google Gemini (Gemini 1.5 Pro, Gemini 1.5 Flash)
   - OpenRouter (single key for multiple models)
3. **Keys are Encrypted**: All API keys are encrypted using Web Crypto API and stored locally in your browser
4. **Never Sent to Server**: API keys are only used for direct client-side API calls

### Usage

1. **Switch to Compare Mode**: Click the "Compare" button in the chat header
2. **Select Providers**: Choose which LLM providers and models to compare
3. **Send Prompt**: Enter your prompt and receive parallel responses from all selected providers
4. **Compare Responses**: View side-by-side comparison of responses with loading states and error handling
5. **Switch Back**: Use "Standard" mode to return to the multi-agent backend chat

### Compare Mode vs Standard Mode

**Compare Mode** makes direct API calls from your browser to the LLM providers. It's designed for comparing raw model responses and doesn't have access to backend features like stock data, uploaded documents, or the multi-agent routing system.

**Standard Mode** uses the TradePal AI backend with full access to real-time stock data, document context from uploaded PDFs, multi-agent routing, and market sentiment analysis. Use Standard mode for trading questions, document-based queries, or when you need access to backend features.

### Security

- API keys are encrypted using AES-GCM encryption
- Keys are stored in browser localStorage (encrypted)
- Encryption keys are stored in sessionStorage (cleared on browser close)
- Keys are never sent to TradePal AI servers
- All API calls are made directly from your browser to the LLM providers

### Supported Providers

When you add an API key for a provider, you can choose from these models:

**OpenAI** (default: `gpt-4-turbo-preview`)
- `gpt-4-turbo-preview` - Latest GPT-4 Turbo model
- `gpt-4` - Standard GPT-4
- `gpt-3.5-turbo` - Fast and cost-effective option

**Anthropic** (default: `claude-3-5-sonnet-20241022`)
- `claude-3-5-sonnet-20241022` - Latest Claude 3.5 Sonnet
- `claude-3-opus-20240229` - Most capable Claude model
- `claude-3-sonnet-20240229` - Balanced performance Claude 3

**Google Gemini** (default: `gemini-1.5-pro`)
- `gemini-1.5-pro` - Most capable Gemini model
- `gemini-1.5-flash` - Faster, lighter version
- `gemini-pro` - Standard Gemini Pro

**OpenRouter** (default: `openai/gpt-4-turbo`)
- `openai/gpt-4-turbo` - GPT-4 Turbo via OpenRouter
- `anthropic/claude-3-opus` - Claude 3 Opus via OpenRouter
- `google/gemini-pro` - Gemini Pro via OpenRouter
- `mistralai/mistral-large` - Mistral Large model
- `x-ai/grok-beta` - Grok beta access

You can select multiple providers and compare their responses side-by-side. Each provider defaults to its recommended model, but you can switch models anytime from the dropdown in the comparison interface.

### Getting API Keys

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **OpenRouter**: https://openrouter.ai/keys

## Development

### Running Tests

```bash
# Backend tests
cd backend
source venv/bin/activate
pip install -r requirements-test.txt
python run_tests.py

# Or with pytest directly
pytest tests/ -v
```

### Code Quality

The codebase follows clean code principles:
- Separation of concerns
- DRY (Don't Repeat Yourself)
- Type safety with TypeScript
- Proper error handling
- Comprehensive documentation

### Adding New Features

1. **New API Endpoint**: Add route in `backend/api/`
2. **New Agent**: Create agent class in `backend/utils/` and add to LangGraph workflow
3. **New Component**: Add component in `frontend/components/`
4. **New Hook**: Add custom hook in `frontend/hooks/`

## Documentation

- [Setup Guide](./SETUP_GUIDE.md) - Detailed setup instructions
- [Testing Guide](./TESTING_GUIDE.md) - How to run and write tests
- [Troubleshooting](./TROUBLESHOOTING.md) - Common issues and solutions
- [Multi-Agent Implementation](./MULTI_AGENT_IMPLEMENTATION.md) - Agent architecture details
- [API Integrations](./backend/API_INTEGRATIONS.md) - External API documentation
- [Verification Report](./VERIFICATION_REPORT.md) - Implementation verification

## Architecture

### Multi-Agent System

The system uses LangGraph to orchestrate multiple specialized agents:

1. **Query arrives** → Orchestrator analyzes intent
2. **Routing decision** → Query sent to appropriate agent
3. **Agent processing** → Agent retrieves context (RAG/CAG) and generates response
4. **Response returned** → Formatted response sent to client

### Retrieval Strategies

- **RAG (Retrieval-Augmented Generation)**: Vector search for dynamic content
- **CAG (Cached-Augmented Generation)**: Pre-loaded context for static content
- **Hybrid RAG/CAG**: Initial RAG, then CAG for subsequent queries

## Production Deployment

### Backend Deployment

1. Set environment variables on hosting platform
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations if needed
4. Start server: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Frontend Deployment

1. Set `NEXT_PUBLIC_API_URL` environment variable
2. Build: `npm run build`
3. Start: `npm start`

### Considerations

- Use environment variables for all secrets
- Enable CORS for production domain
- Set up logging and monitoring
- Configure rate limiting
- Use HTTPS in production

## Contributing

When contributing to this project:

1. Follow existing code style
2. Write tests for new features
3. Update documentation
4. Ensure all tests pass
5. Follow the commit message conventions

## License

See LICENSE file for details.

## Support

For issues and questions:
- Check [Troubleshooting Guide](./TROUBLESHOOTING.md)
- Review [API Documentation](./backend/API_INTEGRATIONS.md)
- Check existing GitHub issues

## Status

**Current Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: December 2024

---

## Notes for Future Development

### Potential Enhancements
- Session persistence across server restarts
- Agent performance metrics and monitoring
- Custom routing rules configuration
- Multi-language support
- Enhanced streaming for all agents
- WebSocket support for real-time updates

### Maintenance Tasks
- Regular dependency updates
- API key rotation procedures
- Database backup strategies
- Performance optimization reviews
- Security audits

### Known Limitations
- ChromaDB uses local storage (consider cloud option for scale)
- Some tests require API keys (use mocks in CI/CD)
- Video demonstration requires manual creation
