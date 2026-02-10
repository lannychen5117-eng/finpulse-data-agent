import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.data.fund import add_subscription, list_subscriptions, analyze_all_subscriptions, remove_subscription, load_subscriptions, save_subscriptions

def test_fund_features():
    print("Starting Fund Feature Test...")
    
    # 1. Clear existing subscriptions
    print("\n1. Clearing subscriptions...")
    save_subscriptions([])
    assert len(list_subscriptions()) == 0
    print("Verified: Subscriptions cleared.")
    
    # 2. Add Funds
    print("\n2. Adding Funds...")
    funds = ["SPY", "2800.HK", "510300.SS"]
    for f in funds:
        res = add_subscription(f)
        print(f"Add {f}: {res}")
        
    current = list_subscriptions()
    print(f"Current subscriptions: {current}")
    assert len(current) == 3
    assert "SPY" in current
    assert "2800.HK" in current
    assert "510300.SS" in current
    print("Verified: All funds added.")
    
    # 3. Analyze Funds
    print("\n3. Running Analysis (this may take a few seconds)...")
    report = analyze_all_subscriptions()
    print("\n--- Analysis Report ---")
    print(report)
    print("-----------------------")
    
    assert "Fund Analysis Report" in report
    assert "SPY" in report
    assert "Price:" in report
    assert "RSI:" in report
    assert "Recommendation:" in report or "Action:" in report
    
    print("\nVerified: Analysis report generated successfully.")
    
    print("\nTest Complete: SUCCESS")

if __name__ == "__main__":
    test_fund_features()
