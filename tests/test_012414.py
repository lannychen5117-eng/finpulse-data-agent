import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.data.fund_loader import get_fund_history

ticker = "012414"
print(f"Testing get_fund_history for {ticker}...")
try:
    df = get_fund_history(ticker, period="6mo")
    print("Result shape:", df.shape)
    print("Head:\n", df.head())
    print("Tail:\n", df.tail())
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
