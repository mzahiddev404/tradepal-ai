"""
Models for stock market API endpoints.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class StockQuoteResponse(BaseModel):
    """Response model for stock quote."""
    symbol: str
    name: Optional[str] = None
    current_price: Optional[float] = None
    previous_close: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[int] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None


class OptionsChainResponse(BaseModel):
    """Response model for options chain."""
    symbol: str
    expiration: Optional[str] = None
    available_expirations: Optional[List[str]] = None
    calls: Optional[List[Dict[str, Any]]] = None
    puts: Optional[List[Dict[str, Any]]] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None


class MarketOverviewResponse(BaseModel):
    """Response model for market overview."""
    indices: Optional[List[Dict[str, Any]]] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None


class HistoricalPriceResponse(BaseModel):
    """Response model for historical stock price."""
    symbol: str
    date: Optional[str] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None
