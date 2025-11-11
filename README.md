# TradePal AI - Professional Trading Assistant

An elegant, AI-powered trading assistant with real-time market data, intelligent chat capabilities, and document processing powered by LangChain and Next.js.

## 🎯 Project Overview

A sophisticated customer service application featuring a multi-agent architecture, real-time stock market integration, advanced retrieval strategies (RAG), and a beautifully designed user interface with a professional teal/emerald color scheme.

## 📋 Current Status

**✅ Core Features Complete**
- Modern, professional UI with teal/emerald color scheme
- Real-time stock market data integration (Yahoo Finance)
- AI-powered chat assistant with LangChain
- PDF document upload and processing
- Market overview dashboard with indices
- Options chain analysis
- Fully refactored and optimized codebase

**🎨 Recent Improvements**
- Replaced generic blue theme with sophisticated teal/emerald palette
- Enhanced UI/UX for professional appearance
- Improved code organization and modularity
- Added comprehensive utility libraries (formatting, validation, constants)
- Better error handling and logging throughout
- Type-safe API interfaces

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

**Frontend**: Next.js 15, TypeScript, Tailwind CSS, shadcn/ui  
**Backend**: FastAPI, LangChain, ChromaDB (optional), yfinance  
**LLMs**: OpenAI GPT-3.5/4  
**Data Sources**: Yahoo Finance (real-time market data)  
**Styling**: Modern teal/emerald color scheme with professional design patterns

## 📚 Documentation

- `IMPLEMENTATION_PLAN.md` - Full development roadmap
- `TROUBLESHOOTING.md` - Common issues & solutions
- `projectspec/` - Project requirements

## ✨ Key Features

- 💬 **Intelligent Chat Assistant**: AI-powered conversations with context awareness
- 📈 **Real-Time Market Data**: Live stock quotes, options chains, and market indices
- 📄 **Document Processing**: Upload and analyze PDF documents
- 🎨 **Professional Design**: Clean, modern interface with sophisticated color palette
- 🔄 **Responsive UI**: Optimized for desktop and mobile devices
- 🛡️ **Type-Safe**: Full TypeScript implementation with strict typing
- ⚡ **Fast & Reliable**: Optimized performance with error handling

## 📈 Progress

- [x] Frontend chatbot with modern UI
- [x] Backend LangChain Agent with stock integration
- [x] PDF upload and processing
- [x] ChromaDB integration
- [x] Stock market data integration
- [x] Complete refactoring and optimization
- [x] Professional color scheme implementation

---

**Status**: Fully Functional ✅ | Production-Ready 🚀

