
import yfinance as yf

tickers = ["SPY", "2800.HK", "510300.SS"]
print(f"Testing tickers: {tickers}")

for t in tickers:
    try:
        stock = yf.Ticker(t)
        hist = stock.history(period="5d")
        if not hist.empty:
            print(f"SUCCESS: {t} - Last close: {hist['Close'].iloc[-1]:.2f}")
        else:
            print(f"FAILURE: {t} - No history found")
    except Exception as e:
        print(f"ERROR: {t} - {e}")
