"""
Smart Flow Analysis service.
Parses options flow data (Cheddar Flow exports) to determine directional bias.
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from utils.chromadb_client import chromadb_client
import io

logger = logging.getLogger(__name__)

class SmartFlowService:
    """
    Service for analyzing options flow data to determine market sentiment.
    Parses tabular data from ChromaDB and computes flow metrics.
    """
    
    def __init__(self):
        self.chromadb = chromadb_client

    def _parse_document_to_dataframe(self, text: str) -> pd.DataFrame:
        """
        Attempts to parse unstructured text into a DataFrame.
        Handles CSV-like structures or space-separated tables common in PDF exports.
        """
        lines = text.split('\n')
        data = []
        
        # Regex to identify a flow row. 
        # Cheddar Flow columns: Time, Ticker, Expiry, Strike, C/P, Spot, Order Type, Prem, ...
        # Example: "09:30:01 TSLA 11/28/25 400 C 395.20 SWEEP $1.2M ..."
        # We'll try to extract key fields: Ticker, Expiry, Strike, Call/Put, Premium, Side (Ask/Bid/Above/Below)
        
        for line in lines:
            # Skip short lines
            if len(line) < 10:
                continue
                
            try:
                row = {}
                
                # 1. Extract Ticker (Simple 2-5 letters)
                # Must filter out common keywords that look like tickers
                ignored_words = {
                    'CALL', 'PUT', 'SWEEP', 'BLOCK', 'SPLIT', 'ASK', 'BID', 'MID', 
                    'ABOVE', 'BELOW', 'OPENING', 'UNUSUAL', 'OTM', 'ITM', 'ATM',
                    'AM', 'PM', 'EST', 'CST', 'PST', 'ET', 'PT', 'JAN', 'FEB', 'MAR',
                    'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC',
                    'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN', 'EXP', 'DTE',
                    'SPOT', 'VOL', 'OI', 'SIDE', 'ORDER', 'TYPE', 'DATE', 'TIME', 'STR', 'TICKER',
                    'ON', 'IN', 'AT', 'OF', 'FOR', 'TO', 'BY', 'WITH', 'DETAILS', 'SHOWED', 'ACTIVITY'
                }
                
                # Find all candidates
                candidates = re.findall(r'\b[A-Z]{1,5}\b', line)
                ticker = None
                for cand in candidates:
                    if cand not in ignored_words and not cand.isdigit():
                        # Assume the first valid non-ignored word is the ticker
                        # Also usually tickers are not just 1 letter 'C' or 'P' unless explicit
                        if len(cand) == 1 and cand in ['C', 'P']: 
                            continue
                        ticker = cand
                        break
                
                if not ticker: continue
                row['symbol'] = ticker
                
                # 2. Extract Date/Expiry (MM/DD/YY or MM/DD/YYYY or YYYY-MM-DD)
                date_match = re.search(r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b', line)
                if date_match:
                    row['expiry'] = date_match.group(1)
                else:
                    # Try YYYY-MM-DD
                    date_match_iso = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', line)
                    if date_match_iso:
                        row['expiry'] = date_match_iso.group(1)
                    else:
                        continue # No expiry found, likely header or garbage
                        
                # 3. Extract Call/Put
                if re.search(r'\b(Call|C)\b', line, re.IGNORECASE):
                    row['put_call'] = 'CALL'
                elif re.search(r'\b(Put|P)\b', line, re.IGNORECASE):
                    row['put_call'] = 'PUT'
                else:
                    continue
                    
                # 4. Extract Premium (e.g., $1.2M, 1.2M, 500k, 50,000)
                # Regex: Optional $ -> digits/commas/dots -> optional K/M/B
                # We need to be careful not to match Strike or Spot price.
                # Premium usually has K/M or is large (>1000).
                # Or it has a $ sign.
                
                # Pattern 1: Explicit $ (Handled well)
                # Pattern 2: Ends with K/M/B (e.g. 1.2M)
                
                prem_match = re.search(r'(?:\$\s?)?([0-9,]+(?:\.\d+)?)\s*([KkMmBb])\b', line)
                if prem_match:
                    # Has multiplier, likely premium
                    raw_val = prem_match.group(1).replace(',', '')
                    val = float(raw_val)
                    multiplier = prem_match.group(2).upper()
                    if multiplier == 'K': val *= 1000
                    if multiplier == 'M': val *= 1000000
                    if multiplier == 'B': val *= 1000000000
                    row['premium'] = val
                else:
                    # Try finding with $ but no multiplier
                    prem_match_dollar = re.search(r'\$\s?([0-9,]+(?:\.\d+)?)', line)
                    if prem_match_dollar:
                        raw_val = prem_match_dollar.group(1).replace(',', '')
                        row['premium'] = float(raw_val)
                    else:
                         row['premium'] = 0.0
                    
                # 5. Extract Strike (Number near Expiry or Call/Put or explicit "Strike: ...")
                # Regex 1: "Strike: 400" (Common in narrative text)
                strike_match_explicit = re.search(r'Strike[:\s]+([0-9,]+(?:\.\d+)?)', line, re.IGNORECASE)
                if strike_match_explicit:
                    row['strike'] = float(strike_match_explicit.group(1).replace(',', ''))
                else:
                    # Regex 2: "400 C" or "400.0 P" (Common in tabular text)
                    strike_match = re.search(r'\b(\d+(?:\.\d+)?)\s+(?:C|P|Call|Put)\b', line, re.IGNORECASE)
                    if strike_match:
                       row['strike'] = float(strike_match.group(1))
                    else:
                       row['strike'] = 0.0

                # 6. Extract Side/Condition (Sweep, Block, Split, Ask, Bid, Above)
                line_upper = line.upper()
                row['side'] = 'UNKNOWN'
                if 'ASK' in line_upper or 'ABOVE' in line_upper:
                    row['side'] = 'ASK'
                elif 'BID' in line_upper or 'BELOW' in line_upper:
                    row['side'] = 'BID'
                elif 'MID' in line_upper:
                    row['side'] = 'MID'
                    
                row['is_sweep'] = 'SWEEP' in line_upper
                
                # 7. Condition flags
                row['conds'] = ''
                if 'UNUSUAL' in line_upper: row['conds'] += 'Unusual '
                if 'OPENING' in line_upper: row['conds'] += 'Opening '
                
                data.append(row)
            except Exception:
                continue
                
        return pd.DataFrame(data)

    def _detect_programs(self, df: pd.DataFrame) -> List[str]:
        """
        Detect algorithmic programs (clusters of trades).
        Criteria: 3+ trades, same expiry/strike/side, within short timeframe (not parsing time yet, so just sequential).
        """
        programs = []
        if df.empty or 'strike' not in df.columns:
            return []
            
        # Group by Expiry, Strike, Side, Put/Call
        grouped = df.groupby(['expiry', 'strike', 'put_call', 'side'])
        for name, group in grouped:
            if len(group) >= 3:
                expiry, strike, put_call, side = name
                # Calculate total premium for this cluster
                cluster_prem = group['premium'].sum()
                if cluster_prem > 100000: # Only meaningful clusters
                    programs.append(f"{put_call} {strike} {expiry} ({len(group)}x)")
        
        return programs[:3] # Top 3

    def analyze_flow(self, ticker: str, df: pd.DataFrame) -> Dict:
        """
        Performs the quantitative analysis on the parsed dataframe.
        """
        if df.empty:
            return {"error": "No flow data found to analyze."}
            
        # Filter for Ticker
        df = df[df['symbol'] == ticker.upper()].copy()
        if df.empty:
            return {"error": f"No flow data found for {ticker}."}
            
        # --- Focus Filters ---
        # 1. Expiry <= 10 days (Front-week)
        # Parse expiry to datetime
        try:
            df['expiry_dt'] = pd.to_datetime(df['expiry'])
            today = datetime.now()
            
            # Robustness: If all expiries are far in future/past, just take the nearest ones?
            days_to_exp = (df['expiry_dt'] - today).dt.days
            unique_expiries = sorted(df['expiry_dt'].unique())
            # front_expiries = unique_expiries[:2] # Original strict filter
            # df = df[df['expiry_dt'].isin(front_expiries)]
            pass # Use all expiries
            
        except Exception as e:
            logger.warning(f"Date parsing failed: {e}")
            pass

        # 2. Premium Filter (Relaxed per user request)
        # We include all trades by default to ensure data visibility.
        # You can re-enable specific thresholds here if needed.
        # df_high_value = df[df['premium'] >= 50000] # Original strict filter
        pass # No filter applied
        
        # --- Key Aggregations ---
        
        # Total Premiums
        bullish_trades = df[(df['put_call'] == 'CALL') & (df['side'].isin(['ASK', 'ABOVE', 'UNKNOWN']))]
        bearish_trades = df[(df['put_call'] == 'PUT') & (df['side'].isin(['ASK', 'ABOVE', 'UNKNOWN']))]
        
        call_prem = bullish_trades['premium'].sum()
        put_prem = bearish_trades['premium'].sum()
        
        total_prem = call_prem + put_prem
        
        # Flow Score
        if total_prem > 0:
            flow_score = (call_prem - put_prem) / total_prem
        else:
            flow_score = 0
            
        # Aggression Ratio
        sweeps = df[df['is_sweep']]
        if not sweeps.empty:
            aggressive_sweeps = sweeps[sweeps['side'].isin(['ASK', 'ABOVE'])]
            aggression_ratio = len(aggressive_sweeps) / len(sweeps)
        else:
            aggression_ratio = 0
            
        # Top Strikes
        key_strikes = []
        if 'strike' in df.columns:
            top_strikes = df.groupby('strike')['premium'].sum().sort_values(ascending=False).head(3)
            key_strikes = [str(s) for s in top_strikes.index.tolist()]
        
        # Dominant Expiry
        if not df.empty:
            dominant_expiry = df['expiry'].mode().iloc[0]
        else:
            dominant_expiry = "N/A"

        # Program Detection
        notable_programs = self._detect_programs(df)
            
        # Recommendation Logic
        bias = "NEUTRAL"
        if flow_score > 0.6:
            bias = "BULLISH"
        elif flow_score < -0.6:
            bias = "BEARISH"
            
        if aggression_ratio > 0.7:
            conviction = "High Conviction"
        else:
            conviction = "Moderate"
            
        rec = "Mixed flow; await clearer signal."
        if bias == "BULLISH":
            rec = f"Flow is Bullish ({flow_score:.2f}). Consider calls/debit spreads."
        elif bias == "BEARISH":
            rec = f"Flow is Bearish ({flow_score:.2f}). Consider puts or defensive posturing."
            
        # Construct Report
        report = {
            "symbol": ticker,
            "bias": bias,
            "flow_score": round(flow_score, 2),
            "aggression_ratio": round(aggression_ratio, 2),
            "call_premium": call_prem,
            "put_premium": put_prem,
            "dominant_expiry": dominant_expiry,
            "key_strikes": key_strikes,
            "notable_programs": notable_programs,
            "recommendation": rec,
            "conviction": conviction
        }
        
        return report

    def run_analysis(self, ticker: str) -> Dict:
        """
        Main entry point.
        """
        try:
            logger.info(f"Starting Smart Flow Analysis for {ticker}")
            if not self.chromadb or not self.chromadb.collection:
                logger.error("ChromaDB collection not available")
                return {"error": "Knowledge Base not available"}

            # 1. Get Documents (Use the fallback scan logic to get raw text)
            results = self.chromadb.collection.get(limit=5) # Get last 5 docs
            
            full_text = ""
            if results and results.get('documents'):
                full_text = "\n".join(results['documents'])
            else:
                logger.warning("No documents found in Knowledge Base")
                return {"error": "No data available in Knowledge Base. Please upload documents."}
                
            # 2. Parse
            df = self._parse_document_to_dataframe(full_text)
            logger.info(f"Parsed {len(df)} rows from documents")
            
            # 3. Analyze
            report = self.analyze_flow(ticker, df)
            
            # If analysis failed, bubble up the error
            if "error" in report:
                return {"error": report["error"]}
            
            return {
                "flow_report": report,
                "raw_data_points": len(df)
            }
            
        except Exception as e:
            logger.error(f"Smart Flow Error: {e}", exc_info=True)
            return {"error": str(e)}

# Replace the global instance
# We will monkey-patch or replace the EventStudyService class with this one
# to avoid changing all imports in api/stock.py for now.
# Or better: We rename the class in this file to EventStudyService but change its methods.

event_study_service = SmartFlowService() 
# Note: This breaks the 'run_event_study' interface! 
# API calls `event_study_service.run_event_study(...)`.
# I must implement `run_event_study` in `SmartFlowService` to maintain API compatibility 
# while returning the new data payload.

class AdapterService(SmartFlowService):
    HOLIDAYS = {} # Placeholder to prevent API crash

    def run_event_study(self, ticker: str, *args, **kwargs) -> Dict:
        # Ignore date args, just run flow analysis
        result = self.run_analysis(ticker)
        
        if result is None:
             return {"symbol": ticker, "error": "Internal Error: Analysis returned None"}

        # If error, ensure symbol is present
        if "error" in result:
            result["symbol"] = ticker
            return result

        # Wrap in a structure that might not break existing typing if strictly checked,
        # but frontend will be updated to read 'flow_report'.
        return {
            "symbol": ticker,
            "flow_report": result["flow_report"],
            "timestamp": datetime.now().isoformat()
        }

event_study_service = AdapterService()
