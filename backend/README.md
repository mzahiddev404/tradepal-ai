# TradePal AI - Backend

FastAPI backend with LangChain agent for customer service AI.

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run server
python main.py
```

Server runs at http://localhost:8000

## API Endpoints

- `POST /api/chat` - Send chat message
- `GET /api/health` - Health check
- `GET /` - API info

## Step 2 Features ✅

- FastAPI server
- LangChain agent with OpenAI
- /chat endpoint
- CORS enabled
- Environment configuration

## Tech Stack

FastAPI • LangChain • OpenAI • Pydantic





