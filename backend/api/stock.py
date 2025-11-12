"""
Stock market data API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging
from models.stock import StockQuoteResponse, OptionsChainResponse, MarketOverviewResponse, HistoricalPriceResponse
from utils.stock_data import stock_data_service
from utils.sentiment_analysis import sentiment_analyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stock", tags=["stock"])


@router.get("/quote/{symbol}", response_model=StockQuoteResponse)
async def get_stock_quote(
    symbol: str,
    include_sentiment: bool = Query(False, description="Include sentiment analysis")
):
    """
    Get current stock quote.
    
    Args:
        symbol: Stock symbol (e.g., SPY, TSLA)
        include_sentiment: Whether to include sentiment analysis
        
    Returns:
        StockQuoteResponse with current quote data
    """
    try:
        symbol_upper = symbol.upper()
        quote = stock_data_service.get_stock_quote(symbol_upper)
        
        if "error" in quote:
            raise HTTPException(
                status_code=404,
                detail=quote["error"]
            )
        
        # Add sentiment if requested
        if include_sentiment:
            try:
                sentiment = sentiment_analyzer.get_stock_sentiment(symbol_upper)
                quote["sentiment"] = sentiment
            except Exception as e:
                logger.warning(f"Could not fetch sentiment for {symbol_upper}: {e}")
                quote["sentiment"] = None
        
        return StockQuoteResponse(**quote)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching stock quote: {str(e)}"
        )


@router.get("/options/{symbol}", response_model=OptionsChainResponse)
async def get_options_chain(
    symbol: str,
    expiration: Optional[str] = Query(None, description="Expiration date (YYYY-MM-DD)")
):
    """
    Get options chain for a stock.
    
    Args:
        symbol: Stock symbol
        expiration: Optional expiration date
        
    Returns:
        OptionsChainResponse with options data
    """
    try:
        symbol_upper = symbol.upper()
        options = stock_data_service.get_options_chain(symbol_upper, expiration)
        
        if "error" in options:
            raise HTTPException(
                status_code=404,
                detail=options["error"]
            )
        
        return OptionsChainResponse(**options)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching options chain: {str(e)}"
        )


@router.get("/market/overview", response_model=MarketOverviewResponse)
async def get_market_overview():
    """
    Get market overview with major indices.
    
    Returns:
        MarketOverviewResponse with market data
    """
    try:
        overview = stock_data_service.get_market_overview()
        
        if "error" in overview:
            raise HTTPException(
                status_code=500,
                detail=overview["error"]
            )
        
        return MarketOverviewResponse(**overview)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching market overview: {str(e)}"
        )


@router.get("/quotes", response_model=List[StockQuoteResponse])
async def get_multiple_quotes(
    symbols: str = Query(..., description="Comma-separated stock symbols")
):
    """
    Get quotes for multiple stocks.
    
    Args:
        symbols: Comma-separated stock symbols (e.g., "SPY,TSLA,AAPL")
        
    Returns:
        List of StockQuoteResponse
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        quotes = stock_data_service.get_multiple_quotes(symbol_list)
        
        return [StockQuoteResponse(**quote) for quote in quotes]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching quotes: {str(e)}"
        )


@router.get("/historical/{symbol}", response_model=HistoricalPriceResponse)
async def get_historical_price(
    symbol: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format")
):
    """
    Get historical stock price for a specific date.
    
    Args:
        symbol: Stock symbol (e.g., SPY, TSLA)
        date: Date in YYYY-MM-DD format
        
    Returns:
        HistoricalPriceResponse with historical price data
    """
    try:
        symbol_upper = symbol.upper()
        historical_data = stock_data_service.get_historical_price(symbol_upper, date)
        
        if "error" in historical_data:
            raise HTTPException(
                status_code=404,
                detail=historical_data["error"]
            )
        
        return HistoricalPriceResponse(**historical_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching historical price: {str(e)}"
        )
