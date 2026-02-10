import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.data.fund_loader import get_fund_history, is_cn_fund

def test_fetch(ticker: str, expected_source: str):
    print(f"\n--- Testing {ticker} (Expected source: {expected_source}) ---")
    
    if expected_source == "akshare":
        assert is_cn_fund(ticker), f"{ticker} should be identified as CN fund"
    else:
        assert not is_cn_fund(ticker), f"{ticker} should NOT be identified as CN fund"
        
    print(f"Is CN Fund? {is_cn_fund(ticker)}")
    
    try:
        df = get_fund_history(ticker, period="1mo")
        if df.empty:
            print(f"❌ Failed to fetch data for {ticker} (Empty DataFrame)")
            return
            
        print(f"✅ Successfully fetched data. Shape: {df.shape}")
        print("Columns:", df.columns.tolist())
        print("Head:\n", df.head(3))
        
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing = [c for c in required_cols if c not in df.columns]
        
        if missing:
            print(f"❌ Missing columns: {missing}")
        else:
            print("✅ All required columns present.")
            
    except Exception as e:
        print(f"❌ Error during fetch: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test US ETF (yfinance)
    test_fetch("SPY", "yfinance")
    
    # Test CN Fund (akshare) - 000001 (China AMC Growth)
    test_fetch("000001", "akshare")
