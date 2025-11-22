"""
Stock market data API endpoints.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
from datetime import datetime
import logging
from models.stock import StockQuoteResponse, OptionsChainResponse, MarketOverviewResponse, HistoricalPriceResponse, HistoricalPriceRangeResponse, EventStudyResponse
from utils.stock_data import stock_data_service
from utils.sentiment_analysis import sentiment_analyzer
from utils.event_study import event_study_service
from utils.holiday_correlations import holiday_correlations

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
            # Return 200 with error in response instead of 404 for better frontend handling
            # Frontend can check for error field
            return StockQuoteResponse(
                symbol=symbol_upper,
                error=quote["error"]
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
    expiration: Optional[str] = Query(None, description="Expiration date (YYYY-MM-DD)"),
    filter_expirations: str = Query("front_week", description="Filter: 'front_week' or 'all'"),
    strike_range: int = Query(5, description="Number of strikes around ATM (3-10)"),
    min_premium: float = Query(50000.0, description="Minimum premium filter in dollars"),
    show_unusual_only: bool = Query(False, description="Show only unusual activity options")
):
    """
    Get options chain for a stock with advanced filtering and unusual activity detection.
    
    Args:
        symbol: Stock symbol
        expiration: Optional expiration date (YYYY-MM-DD)
        filter_expirations: Filter expirations - "front_week" (0DTE to 2 weeks) or "all"
        strike_range: Number of strikes around ATM (default: 5)
        min_premium: Minimum premium filter in dollars (default: 50000)
        show_unusual_only: Only show unusual activity options (default: False)
        
    Returns:
        OptionsChainResponse with options data including unusual activity flags
    """
    try:
        symbol_upper = symbol.upper()
        
        # Validate strike_range
        strike_range = max(3, min(10, strike_range))
        
        options = stock_data_service.get_options_chain(
            symbol_upper, 
            expiration,
            filter_expirations=filter_expirations,
            strike_range=strike_range,
            min_premium=min_premium,
            show_unusual_only=show_unusual_only
        )
        
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


@router.get("/news/{symbol}")
async def get_stock_news(symbol: str):
    """
    Get recent news headlines for a stock symbol.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Dictionary with headlines array
    """
    try:
        from utils.news_fetcher import news_fetcher
        headlines = news_fetcher.get_stock_news(symbol.upper(), max_items=5)
        return {"symbol": symbol.upper(), "headlines": headlines}
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        return {"symbol": symbol.upper(), "headlines": [], "error": str(e)}


@router.get("/put-call-ratio/{symbol}")
async def get_put_call_ratio(symbol: str):
    """
    Get put/call ratio for a stock symbol.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Dictionary with put/call ratio and interpretation
    """
    try:
        ratio_data = stock_data_service.get_put_call_ratio(symbol.upper())
        return ratio_data
    except Exception as e:
        logger.error(f"Error calculating put/call ratio for {symbol}: {e}")
        return {"symbol": symbol.upper(), "error": str(e), "ratio": None, "summary": ""}


@router.get("/unusual-activity/{symbol}")
async def get_unusual_activity_summary(symbol: str):
    """
    Get unusual activity summary for a stock symbol.
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Dictionary with unusual activity summary text
    """
    try:
        summary = stock_data_service.get_unusual_activity_summary(symbol.upper())
        return {"symbol": symbol.upper(), "summary": summary}
    except Exception as e:
        logger.error(f"Error getting unusual activity for {symbol}: {e}")
        return {"symbol": symbol.upper(), "summary": "", "error": str(e)}


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


@router.get("/historical/{symbol}/range", response_model=HistoricalPriceRangeResponse)
async def get_historical_price_range(
    symbol: str,
    days: Optional[int] = Query(5, description="Number of days to look back (default: 5)"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format (defaults to today)")
):
    """
    Get historical stock prices for a date range.
    
    Args:
        symbol: Stock symbol (e.g., SPY, TSLA)
        days: Number of days to look back (default: 5)
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional, defaults to today)
        
    Returns:
        HistoricalPriceRangeResponse with historical price data for the range
    """
    try:
        symbol_upper = symbol.upper()
        
        # Validate days parameter
        if days and days < 1:
            raise HTTPException(status_code=400, detail="Days must be at least 1")
        if days and days > 365:
            raise HTTPException(status_code=400, detail="Days cannot exceed 365")
        
        historical_data = stock_data_service.get_historical_price_range(
            symbol_upper,
            days=days,
            start_date=start_date,
            end_date=end_date
        )
        
        if "error" in historical_data:
            raise HTTPException(
                status_code=404,
                detail=historical_data["error"]
            )
        
        return HistoricalPriceRangeResponse(**historical_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching historical price range: {str(e)}"
        )


@router.get("/event-study/{symbol}", response_model=EventStudyResponse)
async def get_event_study(
    symbol: str,
    start_date: Optional[str] = Query("2017-12-01", description="Start date in YYYY-MM-DD format (default: 2017-12-01)"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format (defaults to today)"),
    windows: Optional[str] = Query(None, description="Event windows as comma-separated pairs like '-5:5,-1:1,0:1'")
):
    """
    Get event study analysis for stock returns around religious holidays.
    
    Analyzes cumulative returns around Jewish High Holidays (Rosh Hashanah, Yom Kippur)
    and Muslim holy windows (Ramadan start/end, Eid al-Fitr, Eid al-Adha) for 2018-2025.
    
    Args:
        symbol: Stock symbol (e.g., SPY, TSLA)
        start_date: Start date in YYYY-MM-DD format (default: 2017-12-01)
        end_date: End date in YYYY-MM-DD format (defaults to today)
        windows: Event windows as comma-separated pairs like '-5:5,-1:1,0:1' (default: -5:5,-1:1,0:1)
        
    Returns:
        EventStudyResponse with summary statistics, bootstrap p-values, and per-event returns
    """
    try:
        symbol_upper = symbol.upper()
        
        # Parse windows if provided
        parsed_windows = None
        if windows:
            try:
                parsed_windows = []
                for w in windows.split(','):
                    parts = w.strip().split(':')
                    if len(parts) == 2:
                        parsed_windows.append((int(parts[0]), int(parts[1])))
                    else:
                        raise ValueError(f"Invalid window format: {w}")
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid windows format: {str(e)}. Use format like '-5:5,-1:1,0:1'"
                )
        
        # Get research-based correlations
        research_insights = {}
        for holiday_name in event_study_service.HOLIDAYS.keys():
            insights = holiday_correlations.format_insights(holiday_name)
            if "error" not in insights:
                research_insights[holiday_name] = insights
        
        # Try to run event study (may fail due to API issues)
        try:
            result = event_study_service.run_event_study(
                ticker=symbol_upper,
                start_date=start_date,
                end_date=end_date,
                windows=parsed_windows
            )
            
            # Add research insights to result
            if "error" not in result:
                result["research_insights"] = research_insights
                result["general_findings"] = holiday_correlations.GENERAL_FINDINGS
                return EventStudyResponse(**result)
            else:
                # If event study fails, return research insights only
                return EventStudyResponse(
                    symbol=symbol_upper,
                    start_date=start_date,
                    end_date=end_date,
                    summary=None,
                    events=None,
                    research_insights=research_insights,
                    general_findings=holiday_correlations.GENERAL_FINDINGS,
                    disclaimers=holiday_correlations.DISCLAIMERS,
                    timestamp=datetime.now().isoformat(),
                    error=f"Live data unavailable: {result['error']}. Showing research-based correlations instead."
                )
        except Exception as e:
            # Return research insights even if event study fails
            return EventStudyResponse(
                symbol=symbol_upper,
                start_date=start_date,
                end_date=end_date,
                summary=None,
                events=None,
                research_insights=research_insights,
                general_findings=holiday_correlations.GENERAL_FINDINGS,
                disclaimers=holiday_correlations.DISCLAIMERS,
                timestamp=datetime.now().isoformat(),
                error=f"Live data calculation failed: {str(e)}. Showing research-based correlations instead."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running event study: {str(e)}"
        )

@router.get("/limits")
async def get_api_limits():
    """
    Get current API usage and limits.
    
    Returns:
        Dictionary with API usage statistics
    """
    return stock_data_service.get_api_usage()
