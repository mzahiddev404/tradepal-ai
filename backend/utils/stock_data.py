"""
Stock market data utilities using yfinance.

This module provides the StockDataService class for fetching real-time stock
market data, options chains, and market overview information.
"""
import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class StockDataService:
    """Service for fetching stock and options data."""
    
    def __init__(self):
        """Initialize the stock data service."""
        pass
    
    def get_stock_quote(self, symbol: str) -> Dict:
        """
        Get current stock quote.
        
        Args:
            symbol: Stock symbol (e.g., 'SPY', 'TSLA')
            
        Returns:
            Dictionary with stock quote data
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price data
            hist = ticker.history(period="1d", interval="1m")
            current_price = hist['Close'].iloc[-1] if not hist.empty else info.get('currentPrice', 0)
            
            return {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "current_price": round(float(current_price), 2),
                "previous_close": round(float(info.get("previousClose", 0)), 2),
                "change": round(float(current_price) - float(info.get("previousClose", 0)), 2),
                "change_percent": round(
                    ((float(current_price) - float(info.get("previousClose", 0))) / float(info.get("previousClose", 1))) * 100,
                    2
                ) if info.get("previousClose") else 0,
                "volume": info.get("volume", 0),
                "market_cap": info.get("marketCap", 0),
                "high_52w": info.get("fiftyTwoWeekHigh", 0),
                "low_52w": info.get("fiftyTwoWeekLow", 0),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching stock quote for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": f"Failed to fetch stock data: {str(e)}"
            }
    
    def get_options_chain(self, symbol: str, expiration: Optional[str] = None) -> Dict:
        """
        Get options chain for a stock.
        
        Args:
            symbol: Stock symbol
            expiration: Optional expiration date (YYYY-MM-DD)
            
        Returns:
            Dictionary with options chain data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get available expiration dates
            expirations = ticker.options
            
            if not expirations:
                return {
                    "symbol": symbol,
                    "error": "No options data available"
                }
            
            # Use provided expiration or nearest one
            if expiration:
                target_exp = expiration
            else:
                # Get nearest expiration (at least 7 days out)
                today = datetime.now().date()
                valid_exps = [exp for exp in expirations if datetime.strptime(exp, "%Y-%m-%d").date() > today + timedelta(days=7)]
                target_exp = valid_exps[0] if valid_exps else expirations[0]
            
            # Get options chain
            opt_chain = ticker.option_chain(target_exp)
            
            # Process calls
            calls = []
            if not opt_chain.calls.empty:
                calls = opt_chain.calls.head(20).to_dict('records')
            
            # Process puts
            puts = []
            if not opt_chain.puts.empty:
                puts = opt_chain.puts.head(20).to_dict('records')
            
            return {
                "symbol": symbol,
                "expiration": target_exp,
                "available_expirations": list(expirations[:10]),  # Limit to 10
                "calls": calls,
                "puts": puts,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": f"Failed to fetch options data: {str(e)}"
            }
    
    def get_market_overview(self) -> Dict:
        """
        Get market overview with major indices.
        
        Returns:
            Dictionary with market overview data
        """
        try:
            indices = {
                "SPY": "S&P 500",
                "QQQ": "NASDAQ 100",
                "DIA": "Dow Jones",
                "IWM": "Russell 2000"
            }
            
            market_data = []
            for symbol, name in indices.items():
                quote = self.get_stock_quote(symbol)
                if "error" not in quote:
                    market_data.append({
                        "symbol": symbol,
                        "name": name,
                        "price": quote.get("current_price", 0),
                        "change": quote.get("change", 0),
                        "change_percent": quote.get("change_percent", 0)
                    })
            
            return {
                "indices": market_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return {
                "error": f"Failed to fetch market data: {str(e)}"
            }
    
    def get_multiple_quotes(self, symbols: List[str]) -> List[Dict]:
        """
        Get quotes for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            List of quote dictionaries
        """
        quotes = []
        for symbol in symbols:
            quote = self.get_stock_quote(symbol)
            quotes.append(quote)
        return quotes


# Global stock data service instance
stock_data_service = StockDataService()
