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
        
        # Format as Markdown Table
        table = "| Indicator | Value |\n|---|---|\n"
        for k, v in summary.items():
            val = f"{v:.2f}" if isinstance(v, float) else f"{v}"
            table += f"| {k} | {val} |\n"
            
        return f"### Technical Analysis for {ticker}\n\n{table}"
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
        
        # Format as Markdown Table
        output = f"### Fundamentals for {ticker}\n\n| Metric | Value |\n|---|---|\n"
        for k, v in metrics.items():
            val = f"{v:.2f}" if isinstance(v, float) else str(v)
            output += f"| {k} | {val} |\n"
            
        if signals:
            output += "\n**Signals:**\n" + "\n".join([f"- {s}" for s in signals])
            
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

from src.data.fund import add_subscription, remove_subscription, list_subscriptions, analyze_all_subscriptions, analyze_fund

@tool
def add_fund_tool(ticker: str) -> str:
    """
    Subscribe to a fund or stock for monitoring.
    Supports US (e.g., SPY), HK (e.g., 2800.HK), and CN funds (e.g., 000001, 510300).
    """
    return add_subscription(ticker)

@tool
def remove_fund_tool(ticker: str) -> str:
    """
    Unsubscribe from a fund or stock.
    """
    return remove_subscription(ticker)

@tool
def list_funds_tool() -> str:
    """
    List all currently subscribed funds.
    """
    funds = list_subscriptions()
    if not funds:
        return "No subscriptions found."
    return f"Subscribed funds: {', '.join(funds)}"

@tool
def analyze_funds_tool() -> str:
    """
    Analyze all subscribed funds and generate a report with Buy/Sell/Hold recommendations.
    """
    return analyze_all_subscriptions()

@tool
def analyze_fund_tool(ticker: str) -> str:
    """
    Analyze a specific fund or stock (no subscription required).
    Supports Chinese funds (e.g., 000001), ETFs, and US stocks.
    Returns price, RSI, MACD, and recommendation.
    """
    result = analyze_fund(ticker)
    if "error" in result:
        return f"Error analyzing {ticker}: {result['error']}"
        
    return (f"Analysis for {result['ticker']}:\n"
            f"Price: {result['price']:.2f}\n"
            f"RSI: {result['rsi']:.2f}\n"
            f"MACD: {result['macd']:.2f}\n"
            f"Recommendation: {result['recommendation']}\n"
            f"Reason: {result['reason']}")

from src.data.futures import get_future_history
from src.analysis.technical import add_technical_indicators

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
        
        return (f"Futures Analysis for {symbol} ({market}):\n"
                f"Price: {price:.2f}\n"
                f"RSI: {rsi:.2f}\n"
                f"MACD: {macd:.2f}\n"
                f"Recommendation: {recommendation}")
    except Exception as e:
        return f"Error analyzing future {symbol}: {e}"

# Export list of tools
TOOLS = [
    stock_price_tool,
    stock_news_tool,
    technical_analysis_tool,
    fundamental_analysis_tool,
    macro_data_tool,
    add_fund_tool,
    remove_fund_tool,
    list_funds_tool,
    analyze_funds_tool,
    analyze_fund_tool,
    analyze_futures_tool
]
