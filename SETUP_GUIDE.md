# Setup Guide - TradePal AI

Quick guide to get both frontend and backend running.

## Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- OpenAI API key

## Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-...

# Run server
python main.py
```

Backend runs at **http://localhost:8000**  
API docs at **http://localhost:8000/docs**

## Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Optional: Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run dev server
npm run dev
```

Frontend runs at **http://localhost:3000**

## Quick Start (Using Scripts)

```bash
# Terminal 1 - Backend
./START_BACKEND.sh

# Terminal 2 - Frontend  
./START_DEV_SERVER.sh
```

## Testing

1. Open http://localhost:3000
2. Type a message in the chat
3. Get AI response from OpenAI via LangChain

## Troubleshooting

**Backend won't start**: Check OPENAI_API_KEY in backend/.env  
**Frontend errors**: Ensure backend is running first  
**macOS Desktop issue**: See TROUBLESHOOTING.md

## What's Working (Steps 1-2)

✅ Next.js chat interface  
✅ FastAPI backend  
✅ LangChain + OpenAI  
✅ Full chat functionality










