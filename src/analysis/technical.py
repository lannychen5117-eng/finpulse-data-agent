import pandas as pd
import numpy as np

def calculate_rsi(series, period=14):
    delta = series.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds technical indicators to the dataframe using pure pandas.
    
    Indicators added:
    - SMA (20, 50, 200)
    - RSI (14)
    - MACD
    - Bollinger Bands
    """
    # Ensure DataFrame is not empty
    if df.empty:
        return df
    
    # Ensure Close is numeric
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')

    # Simple Moving Averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    # RSI
    df['RSI'] = calculate_rsi(df['Close'])
    
    # MACD
    macd, signal = calculate_macd(df['Close'])
    df['MACD'] = macd
    df['MACD_signal'] = signal
    
    # Bollinger Bands
    sma_20 = df['Close'].rolling(window=20).mean()
    std_20 = df['Close'].rolling(window=20).std()
    df['BBL_20_2.0'] = sma_20 - (2 * std_20)
    df['BBM_20_2.0'] = sma_20
    df['BBU_20_2.0'] = sma_20 + (2 * std_20)
        
    return df

def get_analysis_summary(df: pd.DataFrame) -> dict:
    """
    Returns a summary text of the latest indicators.
    """
    if df.empty:
        return {}
        
    last_row = df.iloc[-1]
    
    return {
        "RSI": last_row.get('RSI'),
        "SMA_50": last_row.get('SMA_50'),
        "SMA_200": last_row.get('SMA_200'),
        "Close": last_row['Close']
    }
