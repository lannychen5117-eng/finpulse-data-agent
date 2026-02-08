import yfinance as yf
import pandas as pd

MACRO_TICKERS = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "Nasdaq": "^IXIC",
    "Gold": "GC=F",
    "Crude Oil": "CL=F",
    "10-Year Treasury": "^TNX",
    "DXY (Dollar Index)": "DX-Y.NYB"
}

def get_macro_summary() -> pd.DataFrame:
    """
    Fetches the latest prices for key macroeconomic indicators.
    """
    data = {}
    for name, ticker in MACRO_TICKERS.items():
        t = yf.Ticker(ticker)
        hist = t.history(period="1d")
        if not hist.empty:
            data[name] = hist["Close"].iloc[-1]
        else:
            data[name] = None
    
    return pd.DataFrame(list(data.items()), columns=["Indicator", "Value"])

def get_macro_history(indicator_name: str, period="1y") -> pd.DataFrame:
    """
    Fetches historical data for a specific macro indicator.
    """
    ticker = MACRO_TICKERS.get(indicator_name)
    if not ticker:
        raise ValueError(f"Indicator {indicator_name} not found. Available: {list(MACRO_TICKERS.keys())}")
    
    return yf.Ticker(ticker).history(period=period)

if __name__ == "__main__":
    print("Fetching macro summary...")
    print(get_macro_summary())
