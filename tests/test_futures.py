import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.data.futures import get_future_history

def test_future(symbol, market):
    print(f"Testing {market} Future: {symbol}")
    df = get_future_history(symbol, market)
    if not df.empty:
        print(f"Success! Rows: {len(df)}")
        print(df.tail(3))
    else:
        print("Failed to fetch data.")
    print("-" * 30)

if __name__ == "__main__":
    # Test CN Future (Rebar) -> Symbol might need adjustment depending on akshare version/source
    # standard is usually RB0 for main contract
    test_future("RB0", "CN")
    
    # Test Global Future (Gold)
    test_future("GC=F", "GLOBAL")
