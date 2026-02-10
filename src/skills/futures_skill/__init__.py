from langchain.tools import tool
from src.data.futures import get_future_history
from src.analysis.technical import add_technical_indicators
from src.utils.viz_utils import VizUtils
import pandas as pd

viz = VizUtils()

@tool
def analyze_futures_tool(symbol: str, market: str = "AUTO") -> str:
    """
    Analyze a Futures contract.
    Args:
        symbol: The ticker (e.g., 'RB0' for Rebar, 'GC=F' for Gold).
        market: 'CN', 'GLOBAL', or 'AUTO'.
    """
    try:
        df = get_future_history(symbol, market)
        if df.empty:
            return f"No data found for future: {symbol}"
            
        # Add technicals
        df = add_technical_indicators(df)
        latest = df.iloc[-1]
        
        rsi = latest['RSI']
        macd = latest['MACD']
        price = latest['Close']
        
        recommendation = "HOLD"
        if rsi < 30: recommendation = "BUY"
        elif rsi > 70: recommendation = "SELL"
        elif macd > latest['MACD_signal']: recommendation = "BUY"
        elif macd < latest['MACD_signal']: recommendation = "SELL"
        
        # Create Chart
        chart_path = viz.create_candlestick_chart(df, title=f"{symbol} Futures Price")
        
        return (f"Futures Analysis for {symbol} ({market}):\n"
                f"Price: {price:.2f}\n"
                f"RSI: {rsi:.2f}\n"
                f"MACD: {macd:.2f}\n"
                f"Recommendation: {recommendation}\n"
                f"Chart: {chart_path}")
    except Exception as e:
        return f"Error analyzing future {symbol}: {e}"

TOOLS = [analyze_futures_tool]
