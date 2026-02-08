import yfinance as yf
import pandas as pd
from typing import Dict, Any, List, Optional

def get_stock_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetches historical market data for a given ticker.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., "AAPL").
        period (str): The data period to download (e.g., "1mo", "1y", "ytd", "max").
        interval (str): The data interval (e.g., "1d", "1wk", "1mo").
        
    Returns:
        pd.DataFrame: A DataFrame containing the historical data.
    """
    stock = yf.Ticker(ticker)
    history = stock.history(period=period, interval=interval)
    return history

def get_stock_info(ticker: str) -> Dict[str, Any]:
    """
    Fetches fundamental information about a stock.
    
    Args:
        ticker (str): The stock ticker symbol.
        
    Returns:
        Dict[str, Any]: A dictionary containing stock info.
    """
    stock = yf.Ticker(ticker)
    return stock.info

def get_stock_news(ticker: str) -> List[Dict[str, Any]]:
    """
    Fetches recent news for a specific stock.
    
    Args:
        ticker (str): The stock ticker symbol.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing news items.
    """
    stock = yf.Ticker(ticker)
    return stock.news

if __name__ == "__main__":
    # Simple test
    t = "AAPL"
    print(f"Fetching data for {t}...")
    hist = get_stock_history(t, period="1mo")
    print(f"History shape: {hist.shape}")
    print(f"Latest Close: {hist['Close'].iloc[-1]}")
    
    news = get_stock_news(t)
    print(f"Recent news count: {len(news)}")
    if news:
        print(f"Latest headline: {news[0].get('title')}")
