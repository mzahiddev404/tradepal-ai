# Backend API - TradePal AI

FastAPI backend providing multi-agent AI chat, stock market data, and document processing capabilities.

## Quick Start

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add OPENAI_API_KEY

# Run server
python main.py
```

Server starts on `http://localhost:8000`

## API Endpoints

### Chat
- `POST /api/chat` - Send message to AI agent
- `POST /api/chat/stream` - Streaming chat responses
- `GET /api/health` - Health check

### Stock Data
- `GET /api/stock/quote/{symbol}` - Current stock quote
- `GET /api/stock/quotes?symbols=...` - Multiple quotes
- `GET /api/stock/historical/{symbol}?date=...` - Historical price
- `GET /api/stock/historical/{symbol}/range` - Price range
- `GET /api/stock/options/{symbol}` - Options chain
- `GET /api/stock/market/overview` - Market overview

### Document Upload
- `POST /api/upload` - Upload PDF files for processing
- `GET /api/collection/info` - ChromaDB collection information

### Sentiment Analysis
- `GET /api/sentiment/correlation/{symbol}` - Sentiment-price correlation
- `GET /api/sentiment/correlation/compare` - Compare multiple symbols

## Architecture

### Multi-Agent System

The backend uses LangGraph to orchestrate specialized agents:

1. **Orchestrator Agent** - Routes queries using AWS Bedrock (or OpenAI fallback)
2. **Billing Agent** - Hybrid RAG/CAG for billing questions
3. **Technical Agent** - Pure RAG for technical support
4. **Policy Agent** - Pure CAG for policy documents
5. **General Agent** - Handles stock queries and general conversation

### Retrieval Strategies

- **RAG**: Vector search from ChromaDB for dynamic content
- **CAG**: Pre-loaded context for static documents
- **Hybrid**: Initial RAG, then CAG for subsequent queries

## Configuration

### Environment Variables

Required:
- `OPENAI_API_KEY` - OpenAI API key for LLM

Optional:
- `ALPHA_VANTAGE_API_KEY` - Stock data API (falls back to yfinance)
- `AWS_ACCESS_KEY_ID` - AWS Bedrock access key
- `AWS_SECRET_ACCESS_KEY` - AWS Bedrock secret key
- `AWS_REGION` - AWS region (default: us-east-1)
- `BEDROCK_MODEL_ID` - Bedrock model ID
- `FRONTEND_URL` - Frontend URL for CORS (default: http://localhost:3000)

### ChromaDB

ChromaDB is automatically initialized on first run. Database is stored in `chroma_db/` directory.

To pre-populate with mock data:
```bash
python generate_mock_pdfs.py
python ingest_mock_data.py
```

## Development

### Project Structure

```
backend/
├── api/              # API route handlers
├── core/             # Configuration
├── models/           # Pydantic models
├── utils/            # Business logic and agents
├── tests/            # Test suite
└── main.py          # Application entry point
```

### Running Tests

```bash
pip install -r requirements-test.txt
python run_tests.py
```

### Code Organization

- **api/**: FastAPI route handlers
- **core/**: Application configuration and settings
- **models/**: Pydantic models for request/response validation
- **utils/**: Business logic, agents, and services
- **tests/**: Test suite with fixtures

## Services

### Stock Data Service
- Primary: Alpha Vantage API
- Fallback: yfinance library
- Handles real-time quotes, historical data, options chains

### Sentiment Analysis
- Alpha Vantage News API
- Reddit API integration
- Sentiment correlation analysis

### Document Processing
- PDF text extraction using pdfplumber
- Text chunking and embedding generation
- ChromaDB vector storage

## Error Handling

The backend implements comprehensive error handling:

- Custom exception classes in `utils/exceptions.py`
- HTTP status codes for different error types
- Detailed error messages for debugging
- Fallback mechanisms for external services

## Performance Considerations

- Agent caching for billing queries (CAG)
- Efficient vector search with ChromaDB
- Streaming responses for better UX
- Rate limiting considerations for external APIs

## Security

- Environment variables for all secrets
- CORS configuration for frontend
- Input validation with Pydantic
- Error messages don't expose sensitive information

## Notes for Production

- Use environment variables for all configuration
- Set up proper logging and monitoring
- Configure rate limiting
- Use production-grade database
- Implement backup procedures
- Set up health checks and alerts
