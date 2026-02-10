from langchain.tools import tool
from typing import Optional
import pandas as pd
import json

# Import internal modules
from src.data.stock import get_stock_history, get_stock_news, get_stock_info
from src.analysis.technical import add_technical_indicators, get_analysis_summary
from src.analysis.fundamental import analyze_fundamentals
from src.utils.viz_utils import VizUtils

# Initialize VizUtils
viz = VizUtils()

@tool
def stock_price_tool(ticker: str) -> str:
    """
    Get recent stock price history for a given ticker.
    Returns the latest close price, a brief history summary, and a path to a price chart.
    """
    try:
        df = get_stock_history(ticker, period="3mo")
        if df.empty:
            return f"No data found for {ticker}."
        
        latest = df.iloc[-1]
        
        # Create Chart
        chart_path = viz.create_candlestick_chart(df, title=f"{ticker} Price History (3 Months)")
        
        return (f"Latest data for {ticker}:\n"
                f"Date: {latest.name.date()}\n"
                f"Close: {latest['Close']:.2f}\n"
                f"Volume: {latest['Volume']}\n"
                f"Chart: {chart_path}")
    except Exception as e:
        return f"Error fetching stock price: {e}"

@tool
def stock_news_tool(ticker: str) -> str:
    """
    Get recent news headlines for a given ticker.
    """
    try:
        news = get_stock_news(ticker)
        if not news:
            return f"No news found for {ticker}."
        
        # Format top 5 news items
        summary = ""
        for item in news[:5]:
            summary += f"- {item.get('title')} ({item.get('publisher')})\n"
        return summary
    except Exception as e:
        return f"Error fetching news: {e}"

@tool
def technical_analysis_tool(ticker: str) -> str:
    """
    Perform technical analysis on a stock (RSI, MACD, SMA).
    Returns a summary of indicators and a chart with indicators.
    """
    try:
        df = get_stock_history(ticker, period="6mo")
        if df.empty:
            return f"Not enough data for analysis of {ticker}."
        
        df = add_technical_indicators(df)
        summary = get_analysis_summary(df)
        
        # Create Chart with Indicators (Simplified for now, just close price)
        # TODO: Add separate charts for RSI/MACD if needed
        chart_path = viz.create_line_chart(
            df.reset_index(), 
            x_col='Date', 
            y_cols=['Close', 'SMA_20', 'SMA_50'], 
            title=f"{ticker} Technical Analysis"
        )
        
        return (f"Technical Indicators for {ticker}:\n" + \
               "\n".join([f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}" for k, v in summary.items()]) + \
               f"\nChart: {chart_path}")
    except Exception as e:
        return f"Error in technical analysis: {e}"

@tool
def fundamental_analysis_tool(ticker: str) -> str:
    """
    Get fundamental analysis metrics (P/E, Growth, Margins) for a stock.
    """
    try:
        info = get_stock_info(ticker)
        analysis = analyze_fundamentals(info)
        
        metrics = analysis.get("metrics", {})
        signals = analysis.get("signals", [])
        
        output = f"Fundamentals for {ticker}:\n"
        for k, v in metrics.items():
            val = f"{v:.2f}" if isinstance(v, float) else str(v)
            output += f"- {k}: {val}\n"
            
        if signals:
            output += "\nSignals:\n" + "\n".join([f"- {s}" for s in signals])
            
        return output
    except Exception as e:
        return f"Error in fundamental analysis: {e}"

TOOLS = [
    stock_price_tool,
    stock_news_tool,
    technical_analysis_tool,
    fundamental_analysis_tool
]
