from langchain.tools import tool
from typing import Optional

# Import our internal modules
from src.data.stock import get_stock_history, get_stock_news, get_stock_info
from src.data.macro import get_macro_summary
from src.analysis.technical import add_technical_indicators, get_analysis_summary
from src.analysis.fundamental import analyze_fundamentals

@tool
def stock_price_tool(ticker: str) -> str:
    """
    Get recent stock price history for a given ticker.
    Returns the latest close price and a brief history summary.
    """
    try:
        df = get_stock_history(ticker, period="1mo")
        if df.empty:
            return f"No data found for {ticker}."
        
        latest = df.iloc[-1]
        return f"Latest data for {ticker}:\nDate: {latest.name.date()}\nClose: {latest['Close']:.2f}\nVolume: {latest['Volume']}"
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
        
        # Format top 3 news items
        summary = ""
        for item in news[:3]:
            summary += f"- {item.get('title')} ({item.get('publisher')})\n"
        return summary
    except Exception as e:
        return f"Error fetching news: {e}"

@tool
def technical_analysis_tool(ticker: str) -> str:
    """
    Perform technical analysis on a stock (RSI, MACD, SMA).
    Returns a summary of indicators.
    """
    try:
        df = get_stock_history(ticker, period="6mo")
        if df.empty:
            return f"Not enough data for analysis of {ticker}."
        
        df = add_technical_indicators(df)
        summary = get_analysis_summary(df)
        
        return f"Technical Indicators for {ticker}:\n" + \
               "\n".join([f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}" for k, v in summary.items()])
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

@tool
def macro_data_tool() -> str:
    """
    Get a summary of current macroeconomic indicators (Indices, Gold, Oil).
    """
    try:
        df = get_macro_summary()
        return df.to_string(index=False)
    except Exception as e:
        return f"Error fetching macro data: {e}"

# Export list of tools
TOOLS = [
    stock_price_tool,
    stock_news_tool,
    technical_analysis_tool,
    fundamental_analysis_tool,
    macro_data_tool
]
