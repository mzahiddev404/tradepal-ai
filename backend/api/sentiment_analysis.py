"""
Sentiment correlation analysis API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging
from utils.sentiment_correlation import sentiment_correlation_analyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sentiment", tags=["sentiment-analysis"])


@router.get("/correlation/{symbol}")
async def get_sentiment_correlation(
    symbol: str,
    days: int = Query(30, description="Number of days to analyze", ge=5, le=365)
):
    """
    Analyze correlation between sentiment and price movements for a symbol.
    
    Args:
        symbol: Stock symbol (e.g., TSLA, SPY)
        days: Number of days to analyze (default: 30)
        
    Returns:
        Correlation analysis results
    """
    try:
        symbol_upper = symbol.upper()
        
        # Only allow TSLA and SPY for now
        if symbol_upper not in ["TSLA", "SPY"]:
            raise HTTPException(
                status_code=400,
                detail=f"Analysis currently available for TSLA and SPY only. Requested: {symbol_upper}"
            )
        
        result = sentiment_correlation_analyzer.analyze_correlation(
            symbol=symbol_upper,
            days=days
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=404,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing sentiment correlation for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing correlation: {str(e)}"
        )


@router.get("/correlation/compare")
async def compare_sentiment_correlation(
    symbols: str = Query(..., description="Comma-separated symbols (e.g., TSLA,SPY)"),
    days: int = Query(30, description="Number of days to analyze", ge=5, le=365)
):
    """
    Compare sentiment-price correlation across multiple symbols.
    
    Args:
        symbols: Comma-separated stock symbols (e.g., "TSLA,SPY")
        days: Number of days to analyze (default: 30)
        
    Returns:
        Comparative analysis results
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        
        # Validate symbols
        valid_symbols = ["TSLA", "SPY"]
        invalid_symbols = [s for s in symbol_list if s not in valid_symbols]
        if invalid_symbols:
            raise HTTPException(
                status_code=400,
                detail=f"Analysis currently available for TSLA and SPY only. Invalid: {', '.join(invalid_symbols)}"
            )
        
        if len(symbol_list) < 2:
            raise HTTPException(
                status_code=400,
                detail="Please provide at least 2 symbols for comparison"
            )
        
        result = sentiment_correlation_analyzer.compare_symbols(
            symbols=symbol_list,
            days=days
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing sentiment correlation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing correlation: {str(e)}"
        )





