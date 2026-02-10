import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import yfinance as yf
import pandas as pd
from src.analysis.technical import add_technical_indicators

ticker = "SPY"
print(f"Fetching {ticker}...")
df = yf.download(ticker, period="6mo", interval="1d", progress=False)

print("\nShape:", df.shape)
print("\nColumns:", df.columns)
print("\nHead:\n", df.head())
print("\nClose Column Type:", type(df['Close']))

try:
    print("\nAttempting to add technical indicators...")
    df = add_technical_indicators(df)
    print("Success!")
    print(df[['Close', 'RSI', 'MACD']].tail())
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
