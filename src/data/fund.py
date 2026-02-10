import json
import os
from typing import List, Dict, Any
import yfinance as yf
import pandas as pd
from src.analysis.technical import add_technical_indicators

from src.data.fund_loader import get_fund_history

SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(__file__), '../../data/subscriptions.json')

def load_subscriptions() -> List[str]:
    """Load subscribed tickers from JSON file."""
    if not os.path.exists(SUBSCRIPTIONS_FILE):
        return []
    try:
        with open(SUBSCRIPTIONS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def save_subscriptions(tickers: List[str]):
    """Save subscribed tickers to JSON file."""
    os.makedirs(os.path.dirname(SUBSCRIPTIONS_FILE), exist_ok=True)
    with open(SUBSCRIPTIONS_FILE, 'w') as f:
        json.dump(tickers, f, indent=2)

def add_subscription(ticker: str) -> str:
    """Add a ticker to subscriptions."""
    tickers = load_subscriptions()
    ticker = ticker.upper().strip()
    if ticker not in tickers:
        tickers.append(ticker)
        save_subscriptions(tickers)
        return f"Successfully subscribed to {ticker}."
    return f"Already subscribed to {ticker}."

def remove_subscription(ticker: str) -> str:
    """Remove a ticker from subscriptions."""
    tickers = load_subscriptions()
    ticker = ticker.upper().strip()
    if ticker in tickers:
        tickers.remove(ticker)
        save_subscriptions(tickers)
        return f"Successfully unsubscribed from {ticker}."
    return f"{ticker} was not found in subscriptions."

def list_subscriptions() -> List[str]:
    """List all subscribed tickers."""
    return load_subscriptions()

def analyze_fund(ticker: str) -> Dict[str, Any]:
    """
    Analyze a single fund/stock.
    Returns a dictionary with price, indicators, and recommendation.
    """
    try:
        # Fetch data using unified loader
        df = get_fund_history(ticker, period="6mo")
        
        if df.empty:
            return {"error": f"No data found for {ticker}"}
            
        # Add technical indicators
        df = add_technical_indicators(df)
        latest = df.iloc[-1]
        
        # Simple Strategy Logic
        rsi = latest['RSI']
        macd = latest['MACD']
        signal = latest['MACD_signal']
        close = latest['Close']
        
        recommendation = "HOLD"
        reason = []
        
        # RSI Logic
        if rsi < 30:
            reason.append("RSI is oversold (<30)")
            recommendation = "BUY"
        elif rsi > 70:
            reason.append("RSI is overbought (>70)")
            recommendation = "SELL"
            
        # MACD Logic
        if macd > signal:
            reason.append("MACD is above signal line (Bullish)")
            if recommendation == "HOLD":
                recommendation = "BUY"
        elif macd < signal:
            reason.append("MACD is below signal line (Bearish)")
            if recommendation == "BUY": # Conflict
                recommendation = "HOLD"
                reason.append("Signals conflicting")
            elif recommendation == "HOLD":
                recommendation = "SELL"
                
        return {
            "ticker": ticker,
            "price": float(close),
            "rsi": float(rsi),
            "macd": float(macd),
            "recommendation": recommendation,
            "reason": "; ".join(reason)
        }
        
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

def analyze_all_subscriptions() -> str:
    """Analyze all subscribed funds and return a formatted report."""
    tickers = load_subscriptions()
    if not tickers:
        return "No subscriptions found. Use the 'Subscribe' tool to add funds."
        
    report = ["Fund Analysis Report:", "=" * 30]
    
    for ticker in tickers:
        result = analyze_fund(ticker)
        if "error" in result:
            report.append(f"{ticker}: {result['error']}")
            continue
            
        report.append(f"ticker: {result['ticker']}")
        report.append(f"  Price: {result['price']:.2f}")
        report.append(f"  RSI: {result['rsi']:.2f}")
        report.append(f"  MACD: {result['macd']:.2f}")
        report.append(f"  Action: {result['recommendation']}")
        report.append(f"  Reason: {result['reason']}")
        report.append("-" * 20)
        
    return "\n".join(report)
