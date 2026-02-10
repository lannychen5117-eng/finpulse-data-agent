import akshare as ak
import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional

def get_cn_future_history(symbol: str) -> pd.DataFrame:
    """
    Fetch Chinese Futures Main Contract data using Akshare.
    Symbol example: 'rb0' (Rebar), 'i0' (Iron Ore).
    """
    try:
        # ak.futures_main_sina likes uppercase for some, lowercase for others.
        # usually for sina: V0, P0, B0, M0, I0, RB0... 
        # Let's try upper case generally.
        symbol_upper = symbol.upper()
        
        # This returns Date, Open, High, Low, Close, Volume, etc.
        df = ak.futures_main_sina(symbol=symbol_upper)
        
        if df.empty:
            return pd.DataFrame()
            
        # Rename columns standard
        # '日期' -> Date, '开盘价' -> Open...
        # The columns usually are: 日期, 开盘价, 最高价, 最低价, 收盘价, 成交量, ...
        rename_map = {
            "日期": "Date",
            "开盘价": "Open",
            "最高价": "High",
            "最低价": "Low",
            "收盘价": "Close",
            "成交量": "Volume"
        }
        df.rename(columns=rename_map, inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for c in cols:
            df[c] = pd.to_numeric(df[c])
            
        return df[cols]
    except Exception as e:
        print(f"Error fetching CN future {symbol}: {e}")
        return pd.DataFrame()

def get_global_future_history(symbol: str, period="6mo") -> pd.DataFrame:
    """
    Fetch Global Futures using yfinance.
    Symbol example: 'GC=F' (Gold), 'CL=F' (Crude Oil).
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        print(f"Error fetching Global future {symbol}: {e}")
        return pd.DataFrame()

def get_future_history(symbol: str, market: str = "CN") -> pd.DataFrame:
    """
    Unified fetcher.
    Market: 'CN' or 'GLOBAL'.
    """
    if market == "CN" or (market == "AUTO" and not "=" in symbol):
        return get_cn_future_history(symbol)
    else:
        return get_global_future_history(symbol)

def get_future_info(symbol: str) -> Dict[str, Any]:
    """Basic info wrapper."""
    return {"symbol": symbol, "type": "Future"}
