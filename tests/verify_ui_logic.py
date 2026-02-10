import sys
import os
import re

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.ui.app import extract_ticker
from src.agent.tools import technical_analysis_tool, fundamental_analysis_tool

def test_extract_ticker():
    print("--- Verifying Ticker Extraction ---")
    cases = [
        ("Analyze AAPL stock", "AAPL"),
        ("Check 000001 fund", "000001"),
        ("What about 2800.HK?", "2800.HK"),
        ("Show me RB0 futures", "RB0"),
        ("Is GC=F bullish?", "GC=F"),
        ("How is the weather?", None),
        ("TELL ME ABOUT THIS", None), # Common words ignored
        ("Analyze 510300", "510300")
    ]
    
    for text, expected in cases:
        result = extract_ticker(text)
        status = "✅" if result == expected else f"❌ (Expected {expected}, got {result})"
        print(f"'{text}' -> {result} {status}")

def test_tool_output_format():
    print("\n--- Verifying Tool Output Formats ---")
    
    # Test Technical Analysis Tool
    print("Testing technical_analysis_tool('AAPL')...")
    try:
        tech_out = technical_analysis_tool.invoke("AAPL")
        if "| Indicator | Value |" in tech_out:
            print("✅ Technical Analysis returns Markdown Table.")
        else:
            print("❌ Technical Analysis output format incorrect.")
            print(f"Output snippet: {tech_out[:100]}...")
            
    except Exception as e:
        print(f"⚠️ Error running technical tool: {e}")

    # Test Fundamental Analysis Tool
    print("\nTesting fundamental_analysis_tool('AAPL')...")
    try:
        fund_out = fundamental_analysis_tool.invoke("AAPL")
        if "| Metric | Value |" in fund_out:
            print("✅ Fundamental Analysis returns Markdown Table.")
        else:
            print("❌ Fundamental Analysis output format incorrect.")
            print(f"Output snippet: {fund_out[:100]}...")
            
    except Exception as e:
        print(f"⚠️ Error running fundamental tool: {e}")

if __name__ == "__main__":
    test_extract_ticker()
    test_tool_output_format()
