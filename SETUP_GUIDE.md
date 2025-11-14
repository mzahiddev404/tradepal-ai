# Setup Guide - TradePal AI

Complete setup instructions for getting TradePal AI running on your local machine.

## Prerequisites

Before starting, ensure you have:

- Python 3.13 or higher
- Node.js 18 or higher
- npm or yarn package manager
- Git (for cloning the repository)
- OpenAI API key (required)
- Alpha Vantage API key (optional, system will use yfinance as fallback)

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd tradepal-ai
```

## Step 2: Backend Setup

### 2.1 Create Virtual Environment

```bash
cd backend
python3 -m venv venv
```

### 2.2 Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 2.3 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file and add your API keys:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key-here

# Optional but recommended
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key-here

# Optional - AWS Bedrock for orchestrator
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Frontend URL (default is fine for local dev)
FRONTEND_URL=http://localhost:3000
```

### 2.5 Initialize ChromaDB

ChromaDB will be automatically initialized on first run. The database will be created in `backend/chroma_db/` directory.

### 2.6 (Optional) Load Mock Data

To pre-populate the database with sample documents:

```bash
python generate_mock_pdfs.py
python ingest_mock_data.py
```

### 2.7 Start Backend Server

```bash
python main.py
```

The backend should start on `http://localhost:8000`

Verify it's running:
```bash
curl http://localhost:8000/api/health
```

## Step 3: Frontend Setup

### 3.1 Navigate to Frontend Directory

Open a new terminal window:

```bash
cd frontend
```

### 3.2 Install Dependencies

```bash
npm install
```

### 3.3 Configure Environment Variables

Create `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3.4 Start Development Server

```bash
npm run dev
```

The frontend should start on `http://localhost:3000`

## Step 4: Verify Installation

### 4.1 Check Backend Health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "tradepal-ai-backend"
}
```

### 4.2 Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "history": []}'
```

### 4.3 Open Frontend in Browser

Navigate to `http://localhost:3000` and verify the chat interface loads.

## Common Setup Issues

### Python Version Issues

If you encounter Python version errors:

```bash
# Check Python version
python3 --version

# Use specific version if needed
python3.13 -m venv venv
```

### Node Version Issues

If you encounter Node.js version errors:

```bash
# Check Node version
node --version

# Use nvm to switch versions if needed
nvm install 18
nvm use 18
```

### Port Already in Use

If port 8000 or 3000 is already in use:

**Backend:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in .env
PORT=8001
```

**Frontend:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or change port
npm run dev -- -p 3001
```

### API Key Issues

If you get API key errors:

1. Verify keys are correctly set in `.env`
2. Check for extra spaces or quotes
3. Restart the backend server after changing `.env`
4. Verify API keys are valid and have credits

### ChromaDB Initialization Issues

If ChromaDB fails to initialize:

```bash
# Remove existing database
rm -rf backend/chroma_db/

# Restart backend (will recreate database)
python main.py
```

## Development Workflow

### Running Both Servers

You'll need two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Hot Reload

Both servers support hot reload:
- Backend: Automatically reloads on file changes
- Frontend: Next.js hot reloads on file changes

### Stopping Servers

- Backend: Press `Ctrl+C` in backend terminal
- Frontend: Press `Ctrl+C` in frontend terminal

## Next Steps

After setup is complete:

1. Upload test PDF documents via the frontend
2. Test chat functionality with different query types
3. Explore the multi-agent routing system
4. Review the API documentation
5. Run the test suite

## Additional Resources

- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues and solutions
- [Testing Guide](./TESTING_GUIDE.md) - How to run tests
- [API Documentation](./backend/API_INTEGRATIONS.md) - API reference

## Notes for Production Deployment

When deploying to production:

1. Use environment variables for all secrets (never commit `.env`)
2. Set up proper CORS configuration
3. Configure HTTPS
4. Set up logging and monitoring
5. Use production-grade database (consider ChromaDB cloud)
6. Implement rate limiting
7. Set up backup procedures
8. Configure health checks and alerts
