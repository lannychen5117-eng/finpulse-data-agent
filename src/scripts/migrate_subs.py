import json
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.database.database import get_db
from src.database.models import Subscription, User, MarketType

SUBSCRIPTIONS_FILE = os.path.join(os.path.dirname(__file__), '../../data/subscriptions.json')

def migrate():
    print("Starting migration...")
    
    # 1. Load JSON
    if not os.path.exists(SUBSCRIPTIONS_FILE):
        print("No subscriptions.json found. Skipping.")
        return

    with open(SUBSCRIPTIONS_FILE, 'r') as f:
        tickers = json.load(f)
        
    if not tickers:
        print("No subscriptions to migrate.")
        return

    print(f"Found {len(tickers)} subscriptions: {tickers}")

    # 2. Get DB Session
    db = next(get_db())
    
    # 3. Create a default user if not exists (for migration purposes)
    default_user = db.query(User).filter(User.username == "admin").first()
    if not default_user:
        print("Creating default 'admin' user for migrated data...")
        from werkzeug.security import generate_password_hash
        default_user = User(username="admin", password_hash=generate_password_hash("admin123"), email="admin@finpulse.local")
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
        
    # 4. Migrate Subscriptions
    count = 0
    for ticker in tickers:
        # Determine type crudely
        m_type = MarketType.US_STOCK
        if ".HK" in ticker: m_type = MarketType.HK_STOCK
        elif ".SS" in ticker or ".SZ" in ticker: m_type = MarketType.CN_STOCK
        elif ticker.isdigit() and len(ticker) == 6: m_type = MarketType.CN_STOCK # Fund
        
        exists = db.query(Subscription).filter(
            Subscription.user_id == default_user.id,
            Subscription.symbol == ticker
        ).first()
        
        if not exists:
            sub = Subscription(user_id=default_user.id, symbol=ticker, market_type=m_type)
            db.add(sub)
            count += 1
            
    db.commit()
    print(f"Successfully migrated {count} subscriptions to user 'admin'.")
    db.close()

if __name__ == "__main__":
    migrate()
