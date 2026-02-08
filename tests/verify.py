import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.stock import get_stock_history, get_stock_news, get_stock_info
from src.data.macro import get_macro_summary
from src.agent.tools import stock_price_tool, technical_analysis_tool

def test_data_fetchers():
    print("--- Testing Data Fetchers ---")
    try:
        print("Fetching AAPL history...")
        hist = get_stock_history("AAPL", period="1mo")
        print(f"Success. Shape: {hist.shape}")
        
        print("Fetching AAPL news...")
        news = get_stock_news("AAPL")
        print(f"Success. Count: {len(news)}")
        
        print("Fetching Macro Summary...")
        macro = get_macro_summary()
        print(f"Success.\n{macro}")
    except Exception as e:
        print(f"Data Fetcher Error: {e}")

def test_tools():
    print("\n--- Testing Agent Tools ---")
    try:
        print("Using stock_price_tool for MSFT...")
        res = stock_price_tool.invoke("MSFT")
        print(res[:100] + "...")
        
        print("Using technical_analysis_tool for MSFT...")
        res = technical_analysis_tool.invoke("MSFT")
        print(res)
    except Exception as e:
        print(f"Tool Error: {e}")

if __name__ == "__main__":
    test_data_fetchers()
    test_tools()
