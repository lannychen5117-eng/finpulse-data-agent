import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.database.database import get_db
from src.database.models import User
from src.auth.auth import login_user, register_user
from src.ui.dashboard import get_market_indices
import pandas as pd

print("=== Starting Diagnostics ===")

# 1. Test Database & Auth
print("\n[Test 1] Testing Database & Auth...")
try:
    # Try register a temp user
    reg_res = register_user("diag_user", "diag_pass", "diag@test.com")
    print(f"Register Result: {reg_res}")
    
    # Try login
    login_res = login_user("diag_user", "diag_pass")
    print(f"Login Result: {login_res}")
    
    # Clean up
    if login_res['success']:
        db = next(get_db())
        u = db.query(User).filter(User.username == "diag_user").first()
        if u:
            db.delete(u)
            db.commit()
            print("Cleanup: Deleted diag_user")
        db.close()
except Exception as e:
    print(f"[FAIL] Auth/DB Error: {e}")

# 2. Test Dashboard Data
print("\n[Test 2] Testing YFinance (Dashboard)...")
try:
    df = get_market_indices()
    if not df.empty:
        print(f"[PASS] Retrieved {len(df)} indices.")
        print(df.head())
    else:
        print("[WARN] No indices returned (Check network/yfinance).")
except Exception as e:
    print(f"[FAIL] Dashboard Data Error: {e}")

# 3. Test Agent Init (Simulated)
print("\n[Test 3] Testing Agent Initialization...")
try:
    from src.agent.core import create_agent_executor
    agent = create_agent_executor()
    print("[PASS] Agent Executor created successfully.")
except Exception as e:
    print(f"[FAIL] Agent Init Error: {e}")
    
print("\n=== Diagnostics Complete ===")
