"""
Stock market data utilities using Alpha Vantage (primary) and yfinance (fallback).

This module provides the StockDataService class for fetching real-time stock
market data, options chains, and market overview information.
"""
import yfinance as yf
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import logging
import requests
from core.config import settings

logger = logging.getLogger(__name__)


class StockDataService:
    """Service for fetching stock and options data."""
    
    def __init__(self):
        """Initialize the stock data service."""
        self.alpha_vantage_api_key = settings.alpha_vantage_api_key
        self.use_alpha_vantage = self.alpha_vantage_api_key is not None and len(self.alpha_vantage_api_key) > 0
    
    def _get_alpha_vantage_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get stock quote from Alpha Vantage API.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with quote data or None if failed
        """
        if not self.use_alpha_vantage:
            return None
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.alpha_vantage_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                logger.warning(f"Alpha Vantage error: {data['Error Message']}")
                return None
            
            if "Note" in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return None
            
            quote_data = data.get("Global Quote", {})
            if not quote_data:
                return None
            
            # Parse Alpha Vantage response
            current_price = float(quote_data.get("05. price", 0))
            if current_price == 0:
                return None
            
            previous_close = float(quote_data.get("08. previous close", current_price))
            change = float(quote_data.get("09. change", 0))
            change_percent = float(quote_data.get("10. change percent", "0%").replace("%", ""))
            volume = int(quote_data.get("06. volume", 0))
            high = float(quote_data.get("03. high", current_price))
            low = float(quote_data.get("04. low", current_price))
            open_price = float(quote_data.get("02. open", current_price))
            
            est_tz = ZoneInfo("America/New_York")
            now_est = datetime.now(est_tz)
            
            return {
                "symbol": symbol,
                "name": quote_data.get("01. symbol", symbol),
                "current_price": round(current_price, 2),
                "previous_close": round(previous_close, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": volume,
                "high": round(high, 2),
                "low": round(low, 2),
                "open": round(open_price, 2),
                "timestamp": now_est.isoformat(),
                "data_timestamp": now_est.strftime("%B %d, %Y at %I:%M %p %Z"),
                "source": "Alpha Vantage"
            }
        except Exception as e:
            logger.warning(f"Alpha Vantage API error for {symbol}: {e}")
            return None
    
    def get_stock_quote(self, symbol: str) -> Dict:
        """
        Get current stock quote with most accurate pricing.
        Tries Alpha Vantage first, falls back to yfinance.
        
        Args:
            symbol: Stock symbol (e.g., 'SPY', 'TSLA')
            
        Returns:
            Dictionary with stock quote data
        """
        # Try Alpha Vantage first if available
        if self.use_alpha_vantage:
            alpha_data = self._get_alpha_vantage_quote(symbol)
            if alpha_data:
                logger.info(f"Got quote from Alpha Vantage for {symbol}")
                # Get additional data from yfinance for fields Alpha Vantage doesn't provide
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    alpha_data["market_cap"] = info.get("marketCap", 0)
                    alpha_data["high_52w"] = info.get("fiftyTwoWeekHigh", 0)
                    alpha_data["low_52w"] = info.get("fiftyTwoWeekLow", 0)
                    alpha_data["market_state"] = info.get("marketState", "UNKNOWN")
                    alpha_data["name"] = info.get("longName") or info.get("shortName") or symbol
                except:
                    pass  # Use Alpha Vantage data as-is if yfinance fails
                return alpha_data
            else:
                logger.info(f"Alpha Vantage failed for {symbol}, falling back to yfinance")
        
        # Fallback to yfinance
        try:
            ticker = yf.Ticker(symbol)
            
            # Try multiple methods to get the most current price
            current_price = None
            
            # Method 1: Get recent intraday data (most accurate during market hours)
            try:
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty and len(hist) > 0:
                    current_price = float(hist['Close'].iloc[-1])
                    logger.info(f"Got price from 1min history: ${current_price}")
            except Exception as e:
                logger.warning(f"Could not get 1min history: {e}")
            
            # Method 2: Try 5-day history for more reliable data
            if current_price is None or current_price == 0:
                try:
                    hist = ticker.history(period="5d")
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                        logger.info(f"Got price from 5day history: ${current_price}")
                except Exception as e:
                    logger.warning(f"Could not get 5day history: {e}")
            
            # Method 3: Use info dictionary as fallback
            info = ticker.info
            if current_price is None or current_price == 0:
                current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0)
                logger.info(f"Got price from info: ${current_price}")
            
            # Get previous close for comparison
            previous_close = float(info.get("previousClose", current_price))
            
            # Calculate change
            price_change = current_price - previous_close
            change_percent = (price_change / previous_close * 100) if previous_close > 0 else 0
            
            # Get current datetime in EST timezone
            est_tz = ZoneInfo("America/New_York")
            now_est = datetime.now(est_tz)
            
            return {
                "symbol": symbol,
                "name": info.get("longName") or info.get("shortName") or symbol,
                "current_price": round(float(current_price), 2),
                "previous_close": round(float(previous_close), 2),
                "change": round(float(price_change), 2),
                "change_percent": round(float(change_percent), 2),
                "volume": info.get("volume") or info.get("regularMarketVolume", 0),
                "market_cap": info.get("marketCap", 0),
                "high_52w": info.get("fiftyTwoWeekHigh", 0),
                "low_52w": info.get("fiftyTwoWeekLow", 0),
                "timestamp": now_est.isoformat(),
                "market_state": info.get("marketState", "UNKNOWN"),  # REGULAR, CLOSED, PRE, POST
                "data_timestamp": now_est.strftime("%B %d, %Y at %I:%M %p %Z"),
                "source": "yfinance"
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
                est_tz = ZoneInfo("America/New_York")
                today = datetime.now(est_tz).date()
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
            
            est_tz = ZoneInfo("America/New_York")
            return {
                "symbol": symbol,
                "expiration": target_exp,
                "available_expirations": list(expirations[:10]),  # Limit to 10
                "calls": calls,
                "puts": puts,
                "timestamp": datetime.now(est_tz).isoformat()
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
            
            est_tz = ZoneInfo("America/New_York")
            return {
                "indices": market_data,
                "timestamp": datetime.now(est_tz).isoformat()
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
    
    def _get_alpha_vantage_historical(self, symbol: str, target_date: datetime.date) -> Optional[Dict]:
        """
        Get historical price from Alpha Vantage.
        
        Args:
            symbol: Stock symbol
            target_date: Target date
            
        Returns:
            Dictionary with historical data or None if failed
        """
        if not self.use_alpha_vantage:
            return None
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": self.alpha_vantage_api_key,
                "outputsize": "full"  # Get full history
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data:
                logger.warning(f"Alpha Vantage error: {data['Error Message']}")
                return None
            
            if "Note" in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return None
            
            time_series = data.get("Time Series (Daily)", {})
            if not time_series:
                return None
            
            # Find the closest trading day (may not be exact date due to weekends/holidays)
            date_str = target_date.strftime("%Y-%m-%d")
            
            # Try exact date first
            if date_str in time_series:
                day_data = time_series[date_str]
            else:
                # Find closest previous trading day
                found_date = None
                for ts_date in sorted(time_series.keys(), reverse=True):
                    if ts_date <= date_str:
                        found_date = ts_date
                        break
                
                if not found_date:
                    return None
                
                day_data = time_series[found_date]
                date_str = found_date
            
            est_tz = ZoneInfo("America/New_York")
            now_est = datetime.now(est_tz)
            
            return {
                "symbol": symbol,
                "date": date_str,
                "open": round(float(day_data.get("1. open", 0)), 2),
                "high": round(float(day_data.get("2. high", 0)), 2),
                "low": round(float(day_data.get("3. low", 0)), 2),
                "close": round(float(day_data.get("4. close", 0)), 2),
                "volume": int(day_data.get("5. volume", 0)),
                "timestamp": now_est.isoformat(),
                "data_timestamp": datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y"),
                "source": "Alpha Vantage"
            }
        except Exception as e:
            logger.warning(f"Alpha Vantage historical API error for {symbol}: {e}")
            return None
    
    def get_historical_price(self, symbol: str, date: str) -> Dict:
        """
        Get historical stock price for a specific date.
        Tries Alpha Vantage first, falls back to yfinance.
        
        Args:
            symbol: Stock symbol (e.g., 'SPY', 'TSLA')
            date: Date string in YYYY-MM-DD format or datetime object
            
        Returns:
            Dictionary with historical price data for that date
        """
        try:
            est_tz = ZoneInfo("America/New_York")
            now_est = datetime.now(est_tz)
            
            # Parse date string to datetime
            if isinstance(date, str):
                try:
                    # Try parsing YYYY-MM-DD format first
                    target_date = datetime.strptime(date, "%Y-%m-%d").date()
                except ValueError:
                    try:
                        # Try parsing other common formats
                        from dateutil import parser
                        target_date = parser.parse(date).date()
                    except (ImportError, ValueError):
                        return {
                            "symbol": symbol,
                            "error": f"Invalid date format: {date}. Please use YYYY-MM-DD format."
                        }
            else:
                target_date = date.date() if isinstance(date, datetime) else date
            
            # Check if date is in the future
            if target_date > now_est.date():
                return {
                    "symbol": symbol,
                    "error": f"Date {target_date} is in the future. Cannot fetch historical data for future dates."
                }
            
            # Try Alpha Vantage first if available
            if self.use_alpha_vantage:
                alpha_data = self._get_alpha_vantage_historical(symbol, target_date)
                if alpha_data:
                    logger.info(f"Got historical data from Alpha Vantage for {symbol} on {target_date}")
                    # Get company name from yfinance
                    try:
                        ticker = yf.Ticker(symbol)
                        info = ticker.info
                        alpha_data["name"] = info.get("longName") or info.get("shortName") or symbol
                    except:
                        alpha_data["name"] = symbol
                    return alpha_data
                else:
                    logger.info(f"Alpha Vantage historical failed for {symbol}, falling back to yfinance")
            
            # Fallback to yfinance
            ticker = yf.Ticker(symbol)
            
            # Get historical data for the specific date
            # Use start=date and end=date+1day to get data for that specific day
            start_date = target_date
            end_date = target_date + timedelta(days=1)
            
            hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
            
            if hist.empty:
                # Try to get company info to check if symbol is valid
                try:
                    info = ticker.info
                    # If we can get info but no history, it might be a market holiday or weekend
                    return {
                        "symbol": symbol,
                        "date": target_date.strftime("%Y-%m-%d"),
                        "error": f"No trading data available for {symbol} on {target_date.strftime('%B %d, %Y')}. This may be a market holiday, weekend, or the stock may not have been trading on that date."
                    }
                except:
                    return {
                        "symbol": symbol,
                        "date": target_date.strftime("%Y-%m-%d"),
                        "error": f"Invalid symbol or no data available for {symbol} on {target_date.strftime('%B %d, %Y')}"
                    }
            
            # Get the first (and likely only) row for that date
            row = hist.iloc[0]
            
            # Get company name
            try:
                info = ticker.info
                company_name = info.get("longName") or info.get("shortName") or symbol
            except:
                company_name = symbol
            
            return {
                "symbol": symbol,
                "name": company_name,
                "date": target_date.strftime("%Y-%m-%d"),
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2),
                "volume": int(row['Volume']) if 'Volume' in row else 0,
                "timestamp": now_est.isoformat(),
                "data_timestamp": target_date.strftime("%B %d, %Y"),
                "source": "yfinance"
            }
        except Exception as e:
            logger.error(f"Error fetching historical price for {symbol} on {date}: {e}")
            return {
                "symbol": symbol,
                "date": date if isinstance(date, str) else str(date),
                "error": f"Failed to fetch historical stock data: {str(e)}"
            }


# Global stock data service instance
stock_data_service = StockDataService()
