# TradePal AI - Advanced Customer Service AI

Multi-agent customer service system powered by LangChain, LangGraph, and Next.js.

## 🎯 Project Overview

Proof-of-concept customer service application with multi-agent architecture, advanced retrieval strategies (RAG/CAG), and multi-provider LLM integration.

## 📋 Current Status

**Step 1: Frontend Chatbot** ✅ COMPLETE  
**Step 2: Backend LangChain Agent** ✅ COMPLETE  
**Step 3: Frontend PDF Upload** ✅ COMPLETE
- PDF upload component with drag-and-drop
- File validation and progress tracking
- UI integration

**Next**: Step 4 - ChromaDB & Backend PDF Processing

## 🚀 Quick Start

### Backend
```bash
./START_BACKEND.sh
# Or manually:
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your OPENAI_API_KEY
python main.py
```
API at http://localhost:8000

### Frontend
```bash
./START_DEV_SERVER.sh
# Or manually:
cd frontend
npm install
npm run dev
```
App at http://localhost:3000

**macOS Issue?** See `TROUBLESHOOTING.md` for Turbopack permission errors.

## 📁 Project Structure

```
tradepal-ai/
├── frontend/               # Next.js (Step 1 ✅)
├── backend/               # FastAPI (Step 2 - Coming)
├── projectspec/           # Requirements
└── IMPLEMENTATION_PLAN.md # Roadmap
```

## 🛠️ Tech Stack

**Frontend**: Next.js 16, TypeScript, Tailwind, shadcn/ui  
**Backend** (Coming): FastAPI, LangChain, LangGraph, ChromaDB  
**LLMs**: OpenAI (generation), AWS Bedrock (routing)

## 📚 Documentation

- `IMPLEMENTATION_PLAN.md` - Full development roadmap
- `TROUBLESHOOTING.md` - Common issues & solutions
- `projectspec/` - Project requirements

## 📈 Progress

- [x] Step 1: Frontend chatbot
- [x] Step 2: Backend LangChain Agent
- [x] Step 3: PDF upload
- [ ] Step 4: ChromaDB integration
- [ ] Step 5: RAG implementation
- [ ] Step 6: Multi-agent system

---

**Status**: Steps 1-3 ✅ | Ready for Step 4 🚀

