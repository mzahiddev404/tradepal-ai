"""
FastAPI main application entry point.

This module initializes and configures the FastAPI application with CORS middleware
and routes for chat, upload, and stock market functionality.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router
from api.upload import router as upload_router
from api.stock import router as stock_router
from api.sentiment_analysis import router as sentiment_router
from core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TradePal AI Backend",
    description="Multi-agent customer service AI powered by LangChain",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(stock_router)
app.include_router(sentiment_router)


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    logger.info("Root endpoint accessed")
    return {
        "message": "TradePal AI Backend API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat",
            "health": "/api/health",
            "stock_quote": "/api/stock/quote/{symbol}",
            "market_overview": "/api/stock/market/overview",
            "sentiment_correlation": "/api/sentiment/correlation/{symbol}",
            "compare_sentiment": "/api/sentiment/correlation/compare"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )






