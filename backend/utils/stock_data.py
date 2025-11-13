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
    
    def get_options_chain(
        self, 
        symbol: str, 
        expiration: Optional[str] = None,
        filter_expirations: str = "front_week",
        strike_range: int = 5,
        min_premium: float = 50000.0,
        show_unusual_only: bool = False
    ) -> Dict:
        """
        Get options chain for a stock with advanced filtering and unusual activity detection.
        
        Args:
            symbol: Stock symbol
            expiration: Optional expiration date (YYYY-MM-DD)
            filter_expirations: "front_week" (0DTE to weekly, max 2 weeks) or "all"
            strike_range: Number of strikes around ATM (default: 5)
            min_premium: Minimum premium filter in dollars (default: 50000)
            show_unusual_only: Only show unusual activity options (default: False)
            
        Returns:
            Dictionary with options chain data including unusual activity flags
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get current stock price for ATM calculation
            info = ticker.info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            
            # Get available expiration dates
            expirations = ticker.options
            
            if not expirations:
                return {
                    "symbol": symbol,
                    "error": "No options data available"
                }
            
            est_tz = ZoneInfo("America/New_York")
            today = datetime.now(est_tz).date()
            
            # Filter expirations based on filter_expirations parameter
            if filter_expirations == "front_week":
                # Front week: 0DTE to weekly expiry, max 2 weeks
                filtered_exps = []
                for exp_str in expirations:
                    exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date()
                    dte = (exp_date - today).days
                    if 0 <= dte <= 14:  # 0DTE to 2 weeks
                        filtered_exps.append({
                            "date": exp_str,
                            "dte": dte
                        })
                # Sort by DTE (earliest first)
                filtered_exps.sort(key=lambda x: x["dte"])
            else:
                # All expirations
                filtered_exps = [{"date": exp, "dte": (datetime.strptime(exp, "%Y-%m-%d").date() - today).days} 
                                for exp in expirations[:10]]
                filtered_exps.sort(key=lambda x: x["dte"])
            
            if not filtered_exps:
                return {
                    "symbol": symbol,
                    "error": "No valid expirations found"
                }
            
            # Use provided expiration or earliest filtered one
            if expiration:
                target_exp = expiration
            else:
                target_exp = filtered_exps[0]["date"]
            
            # Get options chain
            opt_chain = ticker.option_chain(target_exp)
            
            # Calculate ATM strike (round to nearest $5 for most stocks, $1 for SPY/QQQ)
            if symbol in ["SPY", "QQQ", "DIA"]:
                atm_strike = round(current_price)
            else:
                atm_strike = round(current_price / 5) * 5
            
            # Process and filter calls
            calls = []
            if not opt_chain.calls.empty:
                calls_df = opt_chain.calls.copy()
                calls_df = self._process_options(
                    calls_df, current_price, atm_strike, strike_range, 
                    min_premium, show_unusual_only, "call"
                )
                calls = calls_df.to_dict('records')
            
            # Process and filter puts
            puts = []
            if not opt_chain.puts.empty:
                puts_df = opt_chain.puts.copy()
                puts_df = self._process_options(
                    puts_df, current_price, atm_strike, strike_range,
                    min_premium, show_unusual_only, "put"
                )
                puts = puts_df.to_dict('records')
            
            # Detect flow patterns
            all_options = calls + puts
            flow_patterns = self._detect_flow_patterns(all_options)
            
            # Update options with flow patterns
            for option in calls + puts:
                strike = option.get("strike", 0)
                option["flow_pattern"] = flow_patterns.get(strike, "isolated")
            
            # Count unusual options
            unusual_count = sum(1 for opt in all_options if opt.get("unusual_activity", False))
            
            return {
                "symbol": symbol,
                "expiration": target_exp,
                "current_price": current_price,
                "atm_strike": atm_strike,
                "strike_range": strike_range,
                "filtered_expirations": filtered_exps,
                "available_expirations": [exp["date"] for exp in filtered_exps],
                "calls": calls,
                "puts": puts,
                "unusual_count": unusual_count,
                "timestamp": datetime.now(est_tz).isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": f"Failed to fetch options data: {str(e)}"
            }
    
    def _process_options(
        self, 
        options_df, 
        current_price: float, 
        atm_strike: float, 
        strike_range: int,
        min_premium: float,
        show_unusual_only: bool,
        option_type: str
    ):
        """Process options dataframe with filtering and unusual activity detection."""
        import pandas as pd
        
        if options_df.empty:
            return options_df
        
        # Filter by strike range (ATM ± strike_range)
        min_strike = atm_strike - (strike_range * 5)  # Assuming $5 increments
        max_strike = atm_strike + (strike_range * 5)
        
        # Adjust for SPY/QQQ which use $1 increments
        if min_strike < 100:
            min_strike = atm_strike - strike_range
            max_strike = atm_strike + strike_range
        
        filtered_df = options_df[
            (options_df["strike"] >= min_strike) & 
            (options_df["strike"] <= max_strike)
        ].copy()
        
        # Calculate metrics
        filtered_df["is_atm"] = abs(filtered_df["strike"] - atm_strike) < 2.5
        
        # Fill NaN values with 0 for numeric columns
        if "volume" in filtered_df.columns:
            filtered_df["volume"] = filtered_df["volume"].fillna(0)
        else:
            filtered_df["volume"] = 0
            
        if "openInterest" in filtered_df.columns:
            filtered_df["openInterest"] = filtered_df["openInterest"].fillna(0)
        else:
            filtered_df["openInterest"] = 0
            
        if "lastPrice" in filtered_df.columns:
            filtered_df["lastPrice"] = filtered_df["lastPrice"].fillna(0)
        else:
            filtered_df["lastPrice"] = 0
        
        # Calculate volume-to-OI ratio
        filtered_df["volume_to_oi_ratio"] = filtered_df.apply(
            lambda row: row["volume"] / row["openInterest"] if row["openInterest"] > 0 else 0,
            axis=1
        )
        
        # Calculate estimated premium (volume × lastPrice × 100)
        filtered_df["estimated_premium"] = filtered_df["volume"] * filtered_df["lastPrice"] * 100
        
        # Detect unusual activity
        filtered_df["unusual_activity"] = False
        filtered_df["activity_reason"] = ""
        
        for idx, row in filtered_df.iterrows():
            reasons = []
            
            # High volume-to-OI ratio
            if row["volume_to_oi_ratio"] > 2.0:
                reasons.append(f"High V/OI ratio ({row['volume_to_oi_ratio']:.2f})")
            
            # Significant premium (use this for detection, but don't filter yet)
            if row["estimated_premium"] >= min_premium:
                reasons.append(f"Premium ${row['estimated_premium']:,.0f}")
            
            # High volume relative to average (if we had historical data)
            if row["volume"] > 100:  # Threshold for significant volume
                reasons.append("High volume")
            
            if reasons:
                filtered_df.at[idx, "unusual_activity"] = True
                filtered_df.at[idx, "activity_reason"] = " | ".join(reasons)
        
        # Filter by minimum premium first (before unusual filter)
        filtered_df = filtered_df[filtered_df["estimated_premium"] >= min_premium]
        
        # Filter by unusual only if requested
        if show_unusual_only:
            filtered_df = filtered_df[filtered_df["unusual_activity"] == True]
        
        return filtered_df
    
    def _detect_flow_patterns(self, options: List[Dict]) -> Dict[float, str]:
        """
        Detect flow patterns across strikes.
        
        Returns:
            Dictionary mapping strike to pattern: "program", "spread", or "isolated"
        """
        patterns = {}
        
        # Group options by strike
        strikes_with_activity = {}
        for opt in options:
            if opt.get("unusual_activity", False):
                strike = opt.get("strike", 0)
                if strike not in strikes_with_activity:
                    strikes_with_activity[strike] = []
                strikes_with_activity[strike].append(opt)
        
        # Detect patterns
        active_strikes = sorted(strikes_with_activity.keys())
        
        for i, strike in enumerate(active_strikes):
            # Check if multiple consecutive strikes are active
            consecutive_count = 1
            for j in range(i + 1, min(i + 4, len(active_strikes))):
                if active_strikes[j] - strike <= 15:  # Within 3 strikes ($15 for $5 increments)
                    consecutive_count += 1
                else:
                    break
            
            if consecutive_count >= 3:
                patterns[strike] = "spread"
            elif len(active_strikes) >= 5:
                patterns[strike] = "program"
            else:
                patterns[strike] = "isolated"
        
        return patterns
    
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
    
    def get_historical_price_range(
        self, 
        symbol: str, 
        days: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Get historical stock prices for a date range.
        
        Args:
            symbol: Stock symbol (e.g., 'SPY', 'TSLA')
            days: Number of days to look back (default: 5)
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional, defaults to today)
            
        Returns:
            Dictionary with historical price data for the date range
        """
        try:
            est_tz = ZoneInfo("America/New_York")
            now_est = datetime.now(est_tz)
            today = now_est.date()
            
            # Determine date range
            if days:
                # Use days parameter
                # Add buffer for weekends/holidays - multiply by 1.5 to ensure we get enough trading days
                buffer_days = max(int(days * 1.5), days + 5)  # At least 5 extra days buffer
                end_date_obj = today
                start_date_obj = today - timedelta(days=buffer_days)
            elif start_date and end_date:
                # Parse provided dates
                try:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                except ValueError:
                    return {
                        "symbol": symbol,
                        "error": "Invalid date format. Use YYYY-MM-DD format."
                    }
            elif start_date:
                # Start date only, end is today
                try:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                    end_date_obj = today
                except ValueError:
                    return {
                        "symbol": symbol,
                        "error": "Invalid date format. Use YYYY-MM-DD format."
                    }
            else:
                # Default to 5 days
                days = 5
                end_date_obj = today
                start_date_obj = today - timedelta(days=days)
            
            # Validate dates
            if start_date_obj > end_date_obj:
                return {
                    "symbol": symbol,
                    "error": "Start date must be before end date."
                }
            
            if end_date_obj > today:
                return {
                    "symbol": symbol,
                    "error": "End date cannot be in the future."
                }
            
            # Limit to reasonable range (max 1 year)
            if (end_date_obj - start_date_obj).days > 365:
                return {
                    "symbol": symbol,
                    "error": "Date range cannot exceed 365 days."
                }
            
            # Try Alpha Vantage first if available
            alpha_prices = None
            if self.use_alpha_vantage:
                try:
                    url = "https://www.alphavantage.co/query"
                    params = {
                        "function": "TIME_SERIES_DAILY",
                        "symbol": symbol,
                        "apikey": self.alpha_vantage_api_key,
                        "outputsize": "compact"
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if "Time Series (Daily)" in data:
                        time_series = data["Time Series (Daily)"]
                        alpha_prices = []
                        for date_str, day_data in sorted(time_series.items()):
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                            if start_date_obj <= date_obj <= end_date_obj:
                                alpha_prices.append({
                                    "date": date_str,
                                    "open": round(float(day_data.get("1. open", 0)), 2),
                                    "high": round(float(day_data.get("2. high", 0)), 2),
                                    "low": round(float(day_data.get("3. low", 0)), 2),
                                    "close": round(float(day_data.get("4. close", 0)), 2),
                                    "volume": int(day_data.get("5. volume", 0))
                                })
                        alpha_prices.reverse()  # Most recent first
                        logger.info(f"Got {len(alpha_prices)} days from Alpha Vantage for {symbol}")
                except Exception as e:
                    logger.warning(f"Alpha Vantage range failed for {symbol}: {e}")
            
            # Fallback to yfinance
            ticker = yf.Ticker(symbol)
            
            # Get historical data for the date range
            # Try with a wider range first to account for weekends/holidays
            hist = ticker.history(
                start=start_date_obj.strftime("%Y-%m-%d"),
                end=(end_date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
            )
            
            # If empty, try extending the range further back
            if hist.empty:
                logger.warning(f"No data for {symbol} in range {start_date_obj} to {end_date_obj}, trying extended range")
                extended_start = start_date_obj - timedelta(days=10)  # Try 10 more days back
                hist = ticker.history(
                    start=extended_start.strftime("%Y-%m-%d"),
                    end=(end_date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
                )
            
            if hist.empty:
                # Try to get company info to check if symbol is valid
                try:
                    info = ticker.info
                    company_name = info.get("longName") or info.get("shortName") or symbol
                    # If we can get info, symbol is valid but no historical data
                    # Check if it's a weekend/holiday issue
                    day_of_week = today.weekday()  # 0=Monday, 6=Sunday
                    if day_of_week >= 5:  # Weekend
                        return {
                            "symbol": symbol,
                            "name": company_name,
                            "error": f"No recent trading data available for {symbol}. The market may be closed (weekend/holiday). Try asking for a specific date or wait until market hours."
                        }
                    else:
                        return {
                            "symbol": symbol,
                            "name": company_name,
                            "error": f"No trading data available for {symbol} in the specified date range. This may be due to market holidays or the symbol may not have been trading during this period. Try a different date range or a specific date."
                        }
                except Exception as e:
                    logger.error(f"Error validating symbol {symbol}: {e}")
                    return {
                        "symbol": symbol,
                        "error": f"Unable to fetch data for {symbol}. Please verify the symbol is correct and try again."
                    }
            
            # Get company name
            try:
                info = ticker.info
                company_name = info.get("longName") or info.get("shortName") or symbol
            except:
                company_name = symbol
            
            # Convert to list of dictionaries (most recent first)
            prices = []
            for date, row in hist.iterrows():
                date_str = date.strftime("%Y-%m-%d")
                # Convert date index to date object
                if hasattr(date, 'date'):
                    date_obj = date.date()
                elif isinstance(date, str):
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                else:
                    try:
                        date_obj = date.to_pydatetime().date()
                    except:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                
                # Filter to requested range (use requested_start_date if available, otherwise start_date_obj)
                filter_start = requested_start_date if 'requested_start_date' in locals() else start_date_obj
                if filter_start <= date_obj <= end_date_obj:
                    prices.append({
                        "date": date_str,
                        "open": round(float(row['Open']), 2),
                        "high": round(float(row['High']), 2),
                        "low": round(float(row['Low']), 2),
                        "close": round(float(row['Close']), 2),
                        "volume": int(row['Volume']) if 'Volume' in row else 0
                    })
            
            # If we still have no prices after filtering, use all available data (up to requested days)
            if not prices and not hist.empty:
                logger.warning(f"No prices in filtered range, using all available recent data")
                filter_start = requested_start_date if 'requested_start_date' in locals() else start_date_obj
                for date, row in hist.iterrows():
                    date_str = date.strftime("%Y-%m-%d")
                    if hasattr(date, 'date'):
                        date_obj = date.date()
                    elif isinstance(date, str):
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    else:
                        try:
                            date_obj = date.to_pydatetime().date()
                        except:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    
                    # Include if within requested range or if it's recent data
                    if date_obj >= filter_start or len(prices) < days:
                        prices.append({
                            "date": date_str,
                            "open": round(float(row['Open']), 2),
                            "high": round(float(row['High']), 2),
                            "low": round(float(row['Low']), 2),
                            "close": round(float(row['Close']), 2),
                            "volume": int(row['Volume']) if 'Volume' in row else 0
                        })
                        if len(prices) >= days:
                            break
            
            # Use Alpha Vantage data if available and more complete
            if alpha_prices and len(alpha_prices) >= len(prices):
                prices = alpha_prices
            
            # If still no prices, return error
            if not prices:
                return {
                    "symbol": symbol,
                    "name": company_name if 'company_name' in locals() else symbol,
                    "error": f"No trading data available for {symbol} in the specified date range. This may be due to market holidays or the symbol may not have been trading during this period."
                }
            
            # Reverse to show oldest first (for trend analysis)
            prices.reverse()
            
            # Use requested start date for response if available
            response_start_date = requested_start_date.strftime("%Y-%m-%d") if 'requested_start_date' in locals() else start_date_obj.strftime("%Y-%m-%d")
            
            return {
                "symbol": symbol,
                "name": company_name,
                "start_date": response_start_date,
                "end_date": end_date_obj.strftime("%Y-%m-%d"),
                "trading_days": len(prices),
                "prices": prices,
                "timestamp": now_est.isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching historical price range for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": f"Failed to fetch historical stock data range: {str(e)}"
            }


# Global stock data service instance
stock_data_service = StockDataService()
