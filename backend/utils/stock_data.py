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
    
    # Fallback prices for when APIs are rate-limited (updated periodically)
    FALLBACK_PRICES = {
        "TSLA": {"price": 242.84, "change": 1.52, "change_percent": 0.63},
        "SPY": {"price": 589.50, "change": 2.30, "change_percent": 0.39},
        "AAPL": {"price": 232.44, "change": 1.12, "change_percent": 0.48},
        "MSFT": {"price": 430.53, "change": 2.05, "change_percent": 0.48},
        "GOOGL": {"price": 175.32, "change": 0.82, "change_percent": 0.47},
        "AMZN": {"price": 210.68, "change": 1.45, "change_percent": 0.69},
        "NVDA": {"price": 138.25, "change": 3.15, "change_percent": 2.33},
        "META": {"price": 584.60, "change": 4.20, "change_percent": 0.72},
    }
    
    def __init__(self):
        """Initialize the stock data service."""
        self.finnhub_api_key = settings.finnhub_api_key
        self.use_finnhub = self.finnhub_api_key is not None and len(self.finnhub_api_key) > 0
        self.alpha_vantage_api_key = settings.alpha_vantage_api_key
        self.use_alpha_vantage = self.alpha_vantage_api_key is not None and len(self.alpha_vantage_api_key) > 0
    
    def _get_finnhub_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get stock quote from Finnhub API.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with quote data or None if failed
        """
        if not self.use_finnhub:
            return None
        
        try:
            # Get real-time quote
            url = "https://finnhub.io/api/v1/quote"
            params = {
                "symbol": symbol,
                "token": self.finnhub_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for valid data
            if not data or data.get("c", 0) == 0:
                logger.warning(f"Finnhub returned no data for {symbol}")
                return None
            
            # Get company profile for name
            profile_url = "https://finnhub.io/api/v1/stock/profile2"
            profile_params = {
                "symbol": symbol,
                "token": self.finnhub_api_key
            }
            
            company_name = symbol
            try:
                profile_response = requests.get(profile_url, params=profile_params, timeout=5)
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    company_name = profile_data.get("name", symbol)
            except:
                pass  # Use symbol if profile fetch fails
            
            # Parse Finnhub response
            # c = current price, d = change, dp = percent change, h = high, l = low, o = open, pc = previous close
            current_price = float(data.get("c", 0))
            previous_close = float(data.get("pc", current_price))
            change = float(data.get("d", 0))
            change_percent = float(data.get("dp", 0))
            high = float(data.get("h", current_price))
            low = float(data.get("l", current_price))
            open_price = float(data.get("o", current_price))
            
            est_tz = ZoneInfo("America/New_York")
            now_est = datetime.now(est_tz)
            
            return {
                "symbol": symbol,
                "name": company_name,
                "current_price": round(current_price, 2),
                "previous_close": round(previous_close, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": 0,  # Finnhub quote doesn't include volume
                "high": round(high, 2),
                "low": round(low, 2),
                "open": round(open_price, 2),
                "timestamp": now_est.isoformat(),
                "data_timestamp": now_est.strftime("%B %d, %Y at %I:%M %p %Z"),
                "source": "Finnhub"
            }
        except Exception as e:
            logger.warning(f"Finnhub API error for {symbol}: {e}")
            return None
    
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
        # Try Finnhub first if available (best rate limits: 60 calls/min)
        if self.use_finnhub:
            finnhub_data = self._get_finnhub_quote(symbol)
            if finnhub_data:
                logger.info(f"Got quote from Finnhub for {symbol}")
                return finnhub_data
            else:
                logger.info(f"Finnhub failed for {symbol}, trying Alpha Vantage")
        
        # Try Alpha Vantage as fallback
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
            info = None
            
            # Method 1: Try to get info first (most reliable) - with retries
            for retry in range(2):
                try:
                    info = ticker.info
                    if info and isinstance(info, dict):
                        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0)
                        if current_price and current_price > 0:
                            logger.info(f"Got price from info: ${current_price}")
                            break
                except Exception as e:
                    if retry == 0:
                        logger.warning(f"Could not get info for {symbol} (attempt {retry+1}): {e}")
                        import time
                        time.sleep(0.5)
                    else:
                        logger.warning(f"Could not get info for {symbol} (attempt {retry+1}): {e}")
            
            # Method 2: Try 1-week history (more reliable than intraday)
            if current_price is None or current_price == 0:
                try:
                    hist = ticker.history(period="1wk")
                    if not hist.empty and len(hist) > 0:
                        current_price = float(hist['Close'].iloc[-1])
                        logger.info(f"Got price from 1week history: ${current_price}")
                except Exception as e:
                    logger.warning(f"Could not get 1week history: {e}")
            
            # Method 3: Try 2-week history
            if current_price is None or current_price == 0:
                try:
                    hist = ticker.history(period="2wk")
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                        logger.info(f"Got price from 2week history: ${current_price}")
                except Exception as e:
                    logger.warning(f"Could not get 2week history: {e}")
            
            # Method 4: Try 1-month history
            if current_price is None or current_price == 0:
                try:
                    hist = ticker.history(period="1mo")
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                        logger.info(f"Got price from 1month history: ${current_price}")
                except Exception as e:
                    logger.warning(f"Could not get 1month history: {e}")
            
            # Method 5: Try 3-month history
            if current_price is None or current_price == 0:
                try:
                    hist = ticker.history(period="3mo")
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                        logger.info(f"Got price from 3month history: ${current_price}")
                except Exception as e:
                    logger.warning(f"Could not get 3month history: {e}")
            
            # Final fallback: Try info again if we still don't have price
            if (current_price is None or current_price == 0) and info is None:
                try:
                    info = ticker.info
                    if info:
                        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0)
                        logger.info(f"Got price from info (fallback): ${current_price}")
                except Exception as e:
                    logger.warning(f"Could not get info (fallback) for {symbol}: {e}")
            
            # If we still don't have info, try one more time
            if info is None:
                try:
                    info = ticker.info
                except Exception as e:
                    logger.error(f"Failed to get ticker info for {symbol}: {e}")
                    raise Exception(f"Unable to fetch current price data for {symbol}. The market data service may be temporarily unavailable.")
            
            # Validate we have a valid price
            if current_price is None or current_price == 0:
                # Last resort - try fetching max history with retry
                for attempt in range(3):
                    try:
                        import time
                        if attempt > 0:
                            time.sleep(1)  # Wait 1 second between retries
                        hist_max = ticker.history(period="1y")
                        if not hist_max.empty:
                            current_price = float(hist_max['Close'].iloc[-1])
                            logger.info(f"Got price from 1year history (attempt {attempt + 1}): ${current_price}")
                            break
                    except Exception as e:
                        logger.warning(f"Could not get 1year history (attempt {attempt + 1}): {e}")
                
                if current_price is None or current_price == 0:
                    # Use fallback prices if available
                    if symbol.upper() in self.FALLBACK_PRICES:
                        fallback = self.FALLBACK_PRICES[symbol.upper()]
                        logger.warning(f"Using fallback price for {symbol}: ${fallback['price']} (APIs are rate-limited)")
                        
                        est_tz = ZoneInfo("America/New_York")
                        now_est = datetime.now(est_tz)
                        
                        return {
                            "symbol": symbol.upper(),
                            "name": symbol.upper(),
                            "current_price": fallback["price"],
                            "previous_close": round(fallback["price"] - fallback["change"], 2),
                            "change": fallback["change"],
                            "change_percent": fallback["change_percent"],
                            "volume": 0,
                            "market_cap": 0,
                            "high_52w": 0,
                            "low_52w": 0,
                            "timestamp": now_est.isoformat(),
                            "market_state": "CLOSED",
                            "data_timestamp": now_est.strftime("%B %d, %Y at %I:%M %p %Z"),
                            "source": "Fallback (APIs rate-limited)"
                        }
                    
                    # Get current EST time for error message
                    est_tz = ZoneInfo("America/New_York")
                    now_est = datetime.now(est_tz)
                    market_status = "The market is currently closed." if now_est.hour < 9 or now_est.hour >= 16 or now_est.weekday() >= 5 else "There may be a temporary issue with the data provider."
                    raise Exception(f"Unable to fetch current price data for {symbol}. {market_status} Note: Both Alpha Vantage and Yahoo Finance APIs are currently rate-limited. Please try again in a few minutes.")
            
            # Get previous close for comparison (with safe defaults)
            previous_close_raw = info.get("previousClose") if info else None
            if previous_close_raw is None:
                previous_close_raw = current_price  # Use current price as fallback
            
            try:
                previous_close = float(previous_close_raw) if previous_close_raw is not None else float(current_price)
            except (ValueError, TypeError):
                previous_close = float(current_price)  # Fallback to current price
            
            # Calculate change
            price_change = float(current_price) - previous_close
            change_percent = (price_change / previous_close * 100) if previous_close > 0 else 0
            
            # Get current datetime in EST timezone
            est_tz = ZoneInfo("America/New_York")
            now_est = datetime.now(est_tz)
            
            # Safely get info fields with defaults
            name = symbol
            volume = 0
            market_cap = 0
            high_52w = 0
            low_52w = 0
            market_state = "UNKNOWN"
            
            if info:
                name = info.get("longName") or info.get("shortName") or symbol
                volume = info.get("volume") or info.get("regularMarketVolume", 0) or 0
                market_cap = info.get("marketCap", 0) or 0
                high_52w = info.get("fiftyTwoWeekHigh", 0) or 0
                low_52w = info.get("fiftyTwoWeekLow", 0) or 0
                market_state = info.get("marketState", "UNKNOWN") or "UNKNOWN"
            
            return {
                "symbol": symbol,
                "name": name,
                "current_price": round(float(current_price), 2),
                "previous_close": round(float(previous_close), 2),
                "change": round(float(price_change), 2),
                "change_percent": round(float(change_percent), 2),
                "volume": int(volume) if volume else 0,
                "market_cap": int(market_cap) if market_cap else 0,
                "high_52w": round(float(high_52w), 2) if high_52w else 0,
                "low_52w": round(float(low_52w), 2) if low_52w else 0,
                "timestamp": now_est.isoformat(),
                "market_state": market_state,
                "data_timestamp": now_est.strftime("%B %d, %Y at %I:%M %p %Z"),
                "source": "yfinance"
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error fetching stock quote for {symbol}: {error_msg}", exc_info=True)
            
            # Provide more helpful error messages
            if "Expecting value" in error_msg or "JSON" in error_msg or "line 1 column 1" in error_msg:
                error_msg = f"Unable to fetch current price data for {symbol}. The market data service may be temporarily unavailable. Please try again in a moment."
            elif "429" in error_msg or "Too Many Requests" in error_msg:
                error_msg = f"Rate limit exceeded while fetching {symbol} data. Please wait a moment and try again."
            elif "delisted" in error_msg.lower():
                error_msg = f"Unable to fetch data for {symbol}. The symbol may be invalid or delisted."
            else:
                error_msg = f"Failed to fetch current price data for {symbol}: {error_msg}"
            
            return {
                "symbol": symbol,
                "error": error_msg
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
            
            # Volume spike detection - compare to average volume across all strikes
            if len(filtered_df) > 1:
                avg_volume = filtered_df["volume"].mean()
                if avg_volume > 0 and row["volume"] > (avg_volume * 2):
                    spike_magnitude = row["volume"] / avg_volume
                    reasons.append(f"Volume spike ({spike_magnitude:.1f}x average)")
            
            if reasons:
                filtered_df.at[idx, "unusual_activity"] = True
                filtered_df.at[idx, "activity_reason"] = " | ".join(reasons)
        
        # Filter by minimum premium first (before unusual filter)
        filtered_df = filtered_df[filtered_df["estimated_premium"] >= min_premium]
        
        # Filter by unusual only if requested
        if show_unusual_only:
            filtered_df = filtered_df[filtered_df["unusual_activity"] == True]
        
        return filtered_df
    
    def get_put_call_ratio(self, symbol: str) -> Dict[str, any]:
        """
        Get put/call ratio and summary for a stock symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with put/call ratio, interpretation, and summary text
        """
        try:
            symbol_upper = symbol.upper()
            
            # Get options chain data
            options_data = self.get_options_chain(
                symbol_upper,
                filter_expirations="front_week",
                strike_range=10,  # Wider range for better ratio calculation
                min_premium=0,  # No premium filter for ratio calculation
                show_unusual_only=False
            )
            
            if "error" in options_data:
                return {
                    "error": options_data["error"],
                    "ratio": None,
                    "interpretation": None,
                    "summary": f"Unable to calculate put/call ratio for {symbol_upper}"
                }
            
            calls = options_data.get("calls", [])
            puts = options_data.get("puts", [])
            
            if not calls and not puts:
                return {
                    "error": "No options data available",
                    "ratio": None,
                    "interpretation": None,
                    "summary": f"No options data available for {symbol_upper}"
                }
            
            # Calculate total volumes
            total_call_volume = sum(opt.get("volume", 0) for opt in calls)
            total_put_volume = sum(opt.get("volume", 0) for opt in puts)
            
            # Calculate ratio
            if total_call_volume > 0:
                ratio = total_put_volume / total_call_volume
            elif total_put_volume > 0:
                ratio = float('inf')  # All puts, no calls
            else:
                ratio = 1.0  # No volume data
            
            # Interpret ratio
            if ratio > 1.5:
                interpretation = "bearish"
                sentiment = "bearish sentiment"
            elif ratio < 0.5:
                interpretation = "bullish"
                sentiment = "bullish sentiment"
            else:
                interpretation = "neutral"
                sentiment = "neutral sentiment"
            
            summary = f"Put/call ratio: {ratio:.2f} ({sentiment})"
            
            return {
                "symbol": symbol_upper,
                "ratio": ratio,
                "put_volume": total_put_volume,
                "call_volume": total_call_volume,
                "interpretation": interpretation,
                "summary": summary
            }
        except Exception as e:
            logger.error(f"Error calculating put/call ratio for {symbol}: {e}")
            return {
                "error": str(e),
                "ratio": None,
                "interpretation": None,
                "summary": f"Error calculating put/call ratio for {symbol_upper}"
            }
    
    def get_unusual_activity_summary(self, symbol: str) -> str:
        """
        Get text summary of unusual options activity for a stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Text summary of unusual activity
        """
        try:
            symbol_upper = symbol.upper()
            
            # Get options chain with unusual activity filter
            options_data = self.get_options_chain(
                symbol_upper,
                filter_expirations="front_week",
                strike_range=5,
                min_premium=50000,
                show_unusual_only=True
            )
            
            if "error" in options_data:
                return ""
            
            calls = options_data.get("calls", [])
            puts = options_data.get("puts", [])
            
            unusual_items = []
            
            # Get top unusual calls
            unusual_calls = sorted(
                [c for c in calls if c.get("unusual_activity", False)],
                key=lambda x: x.get("estimated_premium", 0),
                reverse=True
            )[:2]
            
            for call in unusual_calls:
                strike = call.get("strike", 0)
                premium = call.get("estimated_premium", 0)
                reason = call.get("activity_reason", "")
                unusual_items.append(f"${strike:.0f} calls (Premium ${premium/1000:.0f}K, {reason})")
            
            # Get top unusual puts
            unusual_puts = sorted(
                [p for p in puts if p.get("unusual_activity", False)],
                key=lambda x: x.get("estimated_premium", 0),
                reverse=True
            )[:2]
            
            for put in unusual_puts:
                strike = put.get("strike", 0)
                premium = put.get("estimated_premium", 0)
                reason = put.get("activity_reason", "")
                unusual_items.append(f"${strike:.0f} puts (Premium ${premium/1000:.0f}K, {reason})")
            
            if unusual_items:
                return f"Unusual activity: {', '.join(unusual_items[:3])}"
            else:
                return ""
        except Exception as e:
            logger.error(f"Error getting unusual activity summary for {symbol}: {e}")
            return ""
    
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
            
            # Check if date is in the future (with small buffer for timezone edge cases)
            today = now_est.date()
            
            # Sanity check: if system date seems wrong (more than 1 year in future), use a reasonable max date
            max_reasonable_date = datetime(2024, 12, 31).date()  # End of 2024 as reasonable max
            if today > max_reasonable_date:
                logger.warning(f"System date appears incorrect: {today}. Using {max_reasonable_date} as maximum date.")
                today = max_reasonable_date
            
            if target_date > today:
                return {
                    "symbol": symbol,
                    "date": target_date.strftime("%Y-%m-%d"),
                    "error": f"Cannot fetch historical data for {target_date.strftime('%B %d, %Y')} - this date is in the future. Please use a date on or before {today.strftime('%B %d, %Y')}."
                }
            
            # Check if date is too far in the past (more than 10 years)
            ten_years_ago = today - timedelta(days=3650)
            if target_date < ten_years_ago:
                return {
                    "symbol": symbol,
                    "date": target_date.strftime("%Y-%m-%d"),
                    "error": f"Date {target_date.strftime('%B %d, %Y')} is too far in the past. Historical data is available for the last 10 years."
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
                    company_name = info.get("longName") or info.get("shortName") or symbol
                    
                    # Check if it's a weekend
                    day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
                    if day_of_week >= 5:
                        return {
                            "symbol": symbol,
                            "name": company_name,
                            "date": target_date.strftime("%Y-%m-%d"),
                            "error": f"No trading data available for {symbol} on {target_date.strftime('%B %d, %Y')} - markets are closed on weekends. Please try a weekday date."
                        }
                    
                    # Check if date is today but market hasn't closed yet
                    if target_date == today:
                        current_hour = now_est.hour
                        if current_hour < 16:  # Market closes at 4 PM ET
                            return {
                                "symbol": symbol,
                                "name": company_name,
                                "date": target_date.strftime("%Y-%m-%d"),
                                "error": f"Historical data for today ({target_date.strftime('%B %d, %Y')}) is not yet available. The market closes at 4:00 PM ET. Please check current price or use a past date."
                            }
                    
                    # Otherwise, likely a market holiday or data unavailable
                    return {
                        "symbol": symbol,
                        "name": company_name,
                        "date": target_date.strftime("%Y-%m-%d"),
                        "error": f"No trading data available for {symbol} on {target_date.strftime('%B %d, %Y')}. This may be a market holiday or the stock may not have been trading on that date. Try a different date."
                    }
                except Exception as e:
                    logger.warning(f"Could not validate symbol {symbol}: {e}")
                    return {
                        "symbol": symbol,
                        "date": target_date.strftime("%Y-%m-%d"),
                        "error": f"Unable to fetch data for {symbol} on {target_date.strftime('%B %d, %Y')}. Please verify the symbol is correct and the date is a valid trading day."
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
            requested_start_date = None  # Track the original requested start date for filtering
            if days:
                # Use days parameter
                # Add buffer for weekends/holidays - multiply by 1.5 to ensure we get enough trading days
                buffer_days = max(int(days * 1.5), days + 5)  # At least 5 extra days buffer
                end_date_obj = today
                start_date_obj = today - timedelta(days=buffer_days)
                requested_start_date = today - timedelta(days=days)  # Original requested start
            elif start_date and end_date:
                # Parse provided dates
                try:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                    requested_start_date = start_date_obj  # Use provided start date
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
                    requested_start_date = start_date_obj  # Use provided start date
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
                requested_start_date = start_date_obj  # Use calculated start date
            
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
                filter_start = requested_start_date if requested_start_date is not None else start_date_obj
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
                filter_start = requested_start_date if requested_start_date is not None else start_date_obj
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
            response_start_date = requested_start_date.strftime("%Y-%m-%d") if requested_start_date is not None else start_date_obj.strftime("%Y-%m-%d")
            
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
