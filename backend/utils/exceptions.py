"""
Custom exceptions for better error handling
"""
from typing import Optional


class StockDataError(Exception):
    """Base exception for stock data errors"""
    
    def __init__(self, message: str, symbol: Optional[str] = None, status_code: int = 500):
        self.message = message
        self.symbol = symbol
        self.status_code = status_code
        super().__init__(self.message)


class InvalidSymbolError(StockDataError):
    """Raised when stock symbol is invalid"""
    
    def __init__(self, symbol: str):
        super().__init__(
            f"Invalid stock symbol: {symbol}",
            symbol=symbol,
            status_code=400
        )


class DataUnavailableError(StockDataError):
    """Raised when stock data is unavailable"""
    
    def __init__(self, symbol: str, reason: str = "Data unavailable"):
        super().__init__(
            f"{reason} for {symbol}",
            symbol=symbol,
            status_code=404
        )


class RateLimitError(StockDataError):
    """Raised when API rate limit is exceeded"""
    
    def __init__(self, symbol: Optional[str] = None):
        super().__init__(
            "Rate limit exceeded. Please wait a moment and try again.",
            symbol=symbol,
            status_code=429
        )


class ServiceUnavailableError(StockDataError):
    """Raised when data service is unavailable"""
    
    def __init__(self, symbol: Optional[str] = None):
        super().__init__(
            "Market data service is temporarily unavailable. Please try again later.",
            symbol=symbol,
            status_code=503
        )

