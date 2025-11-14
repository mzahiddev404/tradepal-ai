"""
Event study service for analyzing stock returns around religious holidays.

This module provides functionality to analyze cumulative returns around
Jewish High Holidays and Muslim holy windows using event study methodology.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from utils.stock_data import stock_data_service

logger = logging.getLogger(__name__)


class EventStudyService:
    """Service for performing event studies on stock returns around holidays."""
    
    # Holiday dates for 2018-2025
    HOLIDAYS = {
        # Jewish High Holidays: Rosh Hashanah (first day), Yom Kippur (day)
        'Rosh_Hashanah': [
            '2018-09-10', '2019-09-30', '2020-09-19', '2021-09-07', '2022-09-26',
            '2023-09-16', '2024-10-03', '2025-09-22'
        ],
        'Yom_Kippur': [
            '2018-09-19', '2019-10-09', '2020-09-28', '2021-09-16', '2022-10-05',
            '2023-09-25', '2024-10-12', '2025-10-02'
        ],
        # Muslim windows - approximate Gregorian dates (depends on moon sighting)
        'Ramadan_start': [
            '2018-05-16', '2019-05-06', '2020-04-24', '2021-04-13', '2022-04-02',
            '2023-03-23', '2024-03-11', '2025-03-01'
        ],
        'Ramadan_end': [
            '2018-06-14', '2019-06-04', '2020-05-23', '2021-05-12', '2022-05-01',
            '2023-04-21', '2024-04-09', '2025-03-29'
        ],
        'Eid_al_Fitr': [
            '2018-06-15', '2019-06-05', '2020-05-24', '2021-05-13', '2022-05-02',
            '2023-04-22', '2024-04-10', '2025-03-30'
        ],
        'Eid_al_Adha': [
            '2018-08-22', '2019-08-11', '2020-07-31', '2021-07-20', '2022-07-09',
            '2023-06-28', '2024-06-16', '2025-06-06'
        ]
    }
    
    # Default event windows (inclusive)
    DEFAULT_WINDOWS = [(-5, 5), (-1, 1), (0, 1)]
    
    def __init__(self):
        """Initialize the event study service."""
        pass
    
    def fetch_prices(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        """
        Fetch historical price data for a ticker.
        Uses multiple methods including stock_data_service fallback.
        
        Args:
            ticker: Stock symbol (e.g., 'SPY')
            start: Start date string (YYYY-MM-DD)
            end: End date string (YYYY-MM-DD)
            
        Returns:
            DataFrame with 'price' and 'ret' columns
        """
        import time
        
        # Method 1: Try using period instead of date range (sometimes more reliable)
        try:
            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end)
            days_diff = (end_dt - start_dt).days
            
            # Use period parameter for shorter ranges
            if days_diff <= 365:
                ticker_obj = yf.Ticker(ticker)
                # Try period-based fetch
                if days_diff <= 5:
                    period = '5d'
                elif days_diff <= 30:
                    period = '1mo'
                elif days_diff <= 90:
                    period = '3mo'
                elif days_diff <= 180:
                    period = '6mo'
                else:
                    period = '1y'
                
                df = ticker_obj.history(period=period)
                if not df.empty and len(df) > 0:
                    if 'Close' in df.columns:
                        # Filter to date range
                        df = df[(df.index >= start_dt) & (df.index <= end_dt)]
                        if not df.empty:
                            df = df[['Close']].rename(columns={'Close': 'price'})
                            df['ret'] = df['price'].pct_change()
                            df.index = pd.to_datetime(df.index)
                            logger.info(f"Successfully fetched {len(df)} rows using period method")
                            return df
        except Exception as e:
            logger.debug(f"Period method failed: {e}")
        
        # Method 2: Try yf.download with date range
        import time
        for attempt in range(2):
            try:
                df = yf.download(ticker, start=start, end=end, progress=False, timeout=30, threads=False)
                
                if not df.empty:
                    if 'Adj Close' in df.columns:
                        df = df[['Adj Close']].rename(columns={'Adj Close': 'price'})
                    elif 'Close' in df.columns:
                        df = df[['Close']].rename(columns={'Close': 'price'})
                    else:
                        continue
                    
                    df['ret'] = df['price'].pct_change()
                    df.index = pd.to_datetime(df.index)
                    
                    if len(df) > 0:
                        logger.info(f"Successfully fetched {len(df)} rows using download method")
                        return df
                
                if attempt < 1:
                    time.sleep(2)
                    continue
            except Exception as e:
                logger.debug(f"Download attempt {attempt + 1} failed: {e}")
                if attempt < 1:
                    time.sleep(2)
        
        # Method 3: Try using stock_data_service (has better error handling)
        try:
            logger.info(f"Trying stock_data_service fallback for {ticker}")
            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end)
            days_diff = (end_dt - start_dt).days
            
            # Fetch in chunks if range is large
            all_prices = []
            chunk_size = 365  # 1 year chunks
            
            current_start = start_dt
            while current_start < end_dt:
                current_end = min(current_start + pd.Timedelta(days=chunk_size), end_dt)
                
                price_data = stock_data_service.get_historical_price_range(
                    symbol=ticker,
                    start_date=current_start.strftime('%Y-%m-%d'),
                    end_date=current_end.strftime('%Y-%m-%d')
                )
                
                if 'prices' in price_data and price_data['prices']:
                    for p in price_data['prices']:
                        all_prices.append({
                            'date': pd.to_datetime(p['date']),
                            'price': p['close']
                        })
                
                current_start = current_end + pd.Timedelta(days=1)
            
            if all_prices:
                df = pd.DataFrame(all_prices)
                df.set_index('date', inplace=True)
                df['ret'] = df['price'].pct_change()
                logger.info(f"Successfully fetched {len(df)} rows using stock_data_service")
                return df
        except Exception as e:
            logger.debug(f"stock_data_service method failed: {e}")
        
        # If all methods failed
        raise ValueError(
            f"No data returned for {ticker} from {start} to {end}. "
            f"This may be due to network issues, rate limiting, or invalid date range. "
            f"Please try again in a few moments or check your internet connection."
        )
    
    def get_trading_date_index(self, ts_index: pd.DatetimeIndex, target_date: str) -> Optional[pd.Timestamp]:
        """
        Get the nearest trading date on or before target_date.
        
        Args:
            ts_index: DatetimeIndex of trading dates
            target_date: Target date string (YYYY-MM-DD)
            
        Returns:
            Nearest trading date Timestamp or None
        """
        d = pd.to_datetime(target_date)
        if d in ts_index:
            return d
        
        # If target is weekend/holiday, use next previous trading day
        earlier = ts_index[ts_index <= d]
        if len(earlier) == 0:
            return None
        return earlier[-1]
    
    def calc_cumret(self, price_series: pd.Series, start_date: pd.Timestamp, end_date: pd.Timestamp) -> float:
        """
        Calculate cumulative return between two dates.
        
        Args:
            price_series: Series of prices indexed by date
            start_date: Start date Timestamp
            end_date: End date Timestamp
            
        Returns:
            Cumulative return as float, or np.nan if dates not found
        """
        if start_date not in price_series.index or end_date not in price_series.index:
            return np.nan
        
        p0 = price_series.loc[start_date]
        p1 = price_series.loc[end_date]
        
        if p0 == 0:
            return np.nan
        
        return (p1 / p0) - 1.0
    
    def event_window_return(
        self, 
        prices_df: pd.DataFrame, 
        event_date_str: str, 
        window: Tuple[int, int]
    ) -> float:
        """
        Calculate cumulative return for an event window.
        
        Args:
            prices_df: DataFrame with price data
            event_date_str: Event date string (YYYY-MM-DD)
            window: Tuple of (start_offset, end_offset) days
            
        Returns:
            Cumulative return for the window, or np.nan if calculation fails
        """
        ev = pd.to_datetime(event_date_str)
        idx = prices_df.index
        
        # Find trading dates for event day
        ev_trade = self.get_trading_date_index(idx, event_date_str)
        if ev_trade is None:
            return np.nan
        
        start_dt = ev_trade + pd.Timedelta(days=window[0])
        end_dt = ev_trade + pd.Timedelta(days=window[1])
        
        # Find nearest trading dates on or before start_dt and end_dt
        start_trade = self.get_trading_date_index(idx, start_dt.strftime('%Y-%m-%d'))
        end_trade = self.get_trading_date_index(idx, end_dt.strftime('%Y-%m-%d'))
        
        if start_trade is None or end_trade is None:
            return np.nan
        
        return self.calc_cumret(prices_df['price'], start_trade, end_trade)
    
    def bootstrap_pvals(self, arr: np.ndarray, nboot: int = 5000) -> float:
        """
        Calculate bootstrap p-value for a sample.
        
        Args:
            arr: Array of returns
            nboot: Number of bootstrap iterations
            
        Returns:
            Two-sided bootstrap p-value
        """
        arr = arr[~np.isnan(arr)]
        if len(arr) < 2:
            return np.nan
        
        boot_means = []
        for _ in range(nboot):
            samp = np.random.choice(arr, size=len(arr), replace=True)
            boot_means.append(np.mean(samp))
        
        boot_means = np.array(boot_means)
        obs = np.mean(arr)
        
        # Two-sided p-value
        p = np.mean(np.abs(boot_means) >= abs(obs))
        return p
    
    def run_event_study(
        self,
        ticker: str,
        start_date: str = "2017-12-01",
        end_date: Optional[str] = None,
        windows: Optional[List[Tuple[int, int]]] = None,
        holidays: Optional[Dict[str, List[str]]] = None
    ) -> Dict:
        """
        Run event study analysis.
        
        Args:
            ticker: Stock symbol (e.g., 'SPY')
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD), defaults to today
            windows: List of (start, end) tuples for event windows
            holidays: Dictionary of holiday names to date lists
            
        Returns:
            Dictionary with summary statistics and event-level data
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        if windows is None:
            windows = self.DEFAULT_WINDOWS
        
        if holidays is None:
            holidays = self.HOLIDAYS
        
        try:
            # Validate date range
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date) if end_date else pd.to_datetime(datetime.now())
            
            if start_dt > end_dt:
                return {
                    "error": f"Invalid date range: start_date ({start_date}) must be before end_date ({end_date})"
                }
            
            # Limit date range to reasonable bounds (max 10 years)
            max_range_days = 3650
            if (end_dt - start_dt).days > max_range_days:
                logger.warning(f"Date range exceeds {max_range_days} days, limiting to last 10 years")
                start_dt = end_dt - pd.Timedelta(days=max_range_days)
                start_date = start_dt.strftime('%Y-%m-%d')
            
            # Fetch price data
            logger.info(f"Fetching price data for {ticker} from {start_date} to {end_date}")
            prices = self.fetch_prices(ticker, start_date, end_date)
            
            if prices.empty:
                return {
                    "error": f"No price data available for {ticker} in the specified date range ({start_date} to {end_date}). Please check the symbol and date range."
                }
            
            logger.info(f"Price data from {prices.index[0].date()} to {prices.index[-1].date()}")
            
            # Calculate returns for all events
            rows = []
            for holiday_name, dates in holidays.items():
                for d in dates:
                    # Only process dates within our data range
                    event_date = pd.to_datetime(d)
                    if event_date < prices.index[0] or event_date > prices.index[-1]:
                        continue
                    
                    for w in windows:
                        r = self.event_window_return(prices, d, w)
                        rows.append({
                            'holiday': holiday_name,
                            'event_date': d,
                            'window': f"{w[0]}..{w[1]}",
                            'cum_return': r
                        })
            
            if not rows:
                return {
                    "error": "No events found in the specified date range"
                }
            
            df_events = pd.DataFrame(rows)
            df_events['cum_return'] = df_events['cum_return'].astype(float)
            
            # Summary statistics by holiday & window
            summary = df_events.groupby(['holiday', 'window'])['cum_return'].agg(['count', 'mean', 'std'])
            summary['t_stat'] = summary['mean'] / (summary['std'] / np.sqrt(summary['count']))
            summary = summary.reset_index()
            
            # Calculate bootstrap p-values
            pvals = []
            for (h, w), grp in df_events.groupby(['holiday', 'window']):
                p = self.bootstrap_pvals(grp['cum_return'].values, nboot=2000)
                pvals.append({
                    'holiday': h,
                    'window': w,
                    'bootstrap_p': p,
                    'n': grp['cum_return'].count()
                })
            
            pvals_df = pd.DataFrame(pvals)
            
            # Merge summary and p-values
            out = summary.merge(
                pvals_df,
                left_on=['holiday', 'window'],
                right_on=['holiday', 'window']
            )
            
            # Convert to dict format for JSON serialization
            summary_list = out.to_dict('records')
            
            # Format for response
            for record in summary_list:
                # Round numeric values
                record['mean'] = round(record['mean'], 6) if not pd.isna(record['mean']) else None
                record['std'] = round(record['std'], 6) if not pd.isna(record['std']) else None
                record['t_stat'] = round(record['t_stat'], 4) if not pd.isna(record['t_stat']) else None
                record['bootstrap_p'] = round(record['bootstrap_p'], 4) if not pd.isna(record['bootstrap_p']) else None
                record['count'] = int(record['count'])
                record['n'] = int(record['n'])
            
            # Format events list
            events_list = df_events.to_dict('records')
            for event in events_list:
                event['cum_return'] = round(event['cum_return'], 6) if not pd.isna(event['cum_return']) else None
            
            return {
                "symbol": ticker.upper(),
                "start_date": start_date,
                "end_date": end_date,
                "summary": summary_list,
                "events": events_list,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error running event study for {ticker}: {e}", exc_info=True)
            return {
                "error": f"Failed to run event study: {str(e)}"
            }


# Global event study service instance
event_study_service = EventStudyService()

