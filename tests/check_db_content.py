import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.database.database import get_db
from src.database.models import User, Subscription
from sqlalchemy import text

print("Checking database connection...")

try:
    db = next(get_db())
    # Test simple query
    db.execute(text("SELECT 1"))
    print("Connection successful.")
    
    # Check Users
    img_users = db.query(User).all()
    print(f"Users found: {len(img_users)}")
    for u in img_users:
        print(f" - ID: {u.id}, Username: {u.username}, Email: {u.email}")
        
    # Check Subscriptions
    subs = db.query(Subscription).all()
    print(f"Subscriptions found: {len(subs)}")
    for s in subs:
        print(f" - User: {s.user.username}, Symbol: {s.symbol}")
        
    db.close()
except Exception as e:
    print(f"Error connecting/querying database: {e}")
    import traceback
    traceback.print_exc()
