import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.agent.tools import TOOLS, analyze_fund_tool

def test_tool_registration():
    print("--- Verifying Tool Registration ---")
    tool_names = [t.name for t in TOOLS]
    print(f"Available tools: {tool_names}")
    
    if "analyze_fund_tool" in tool_names:
        print("✅ analyze_fund_tool is registered.")
    else:
        print("❌ analyze_fund_tool is NOT registered.")

def test_tool_execution():
    print("\n--- Verifying Tool Execution ---")
    ticker = "000001"
    print(f"Running analyze_fund_tool('{ticker}')...")
    
    try:
        result = analyze_fund_tool.invoke(ticker)
        print(f"Result:\n{result}")
        
        if "Analysis for 000001" in result and "Price:" in result:
             print("✅ Tool execution successful.")
        else:
             print("❌ Tool execution failed validation.")
             
    except Exception as e:
        print(f"❌ Tool execution error: {e}")

if __name__ == "__main__":
    test_tool_registration()
    test_tool_execution()
