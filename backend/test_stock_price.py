#!/usr/bin/env python3
"""
Test script to verify stock price fetching accuracy.
Run this to see exactly what data is being retrieved.
"""
import sys
from utils.stock_data import stock_data_service
from datetime import datetime
from zoneinfo import ZoneInfo

def test_stock_price(symbol: str):
    """Test stock price retrieval for a given symbol."""
    est_tz = ZoneInfo("America/New_York")
    print(f"\n{'='*70}")
    print(f"Testing Stock Data Retrieval for: {symbol}")
    print(f"Time (EST): {datetime.now(est_tz).strftime('%B %d, %Y at %I:%M %p %Z')}")
    print(f"{'='*70}\n")
    
    data = stock_data_service.get_stock_quote(symbol)
    
    if "error" in data:
        print(f"❌ ERROR: {data['error']}\n")
        return
    
    print(f"✅ Successfully retrieved data for {symbol}\n")
    print(f"Company: {data.get('name', 'N/A')}")
    print(f"Symbol: {data.get('symbol', 'N/A')}")
    print(f"\n{'─'*70}")
    print(f"CURRENT PRICE: ${data.get('current_price', 0):.2f}")
    print(f"{'─'*70}\n")
    print(f"Previous Close: ${data.get('previous_close', 0):.2f}")
    print(f"Change: ${data.get('change', 0):.2f} ({data.get('change_percent', 0):+.2f}%)")
    print(f"Volume: {data.get('volume', 0):,}")
    print(f"Market Cap: ${data.get('market_cap', 0):,}")
    print(f"52W High: ${data.get('high_52w', 0):.2f}")
    print(f"52W Low: ${data.get('low_52w', 0):.2f}")
    print(f"Market State: {data.get('market_state', 'UNKNOWN')}")
    print(f"Data Timestamp: {data.get('data_timestamp', 'N/A')}")
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    # Test with command line argument or default symbols
    symbols = sys.argv[1:] if len(sys.argv) > 1 else ["AAPL", "TSLA", "SPY"]
    
    for symbol in symbols:
        test_stock_price(symbol.upper())
        print()

