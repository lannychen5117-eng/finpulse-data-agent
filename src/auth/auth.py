from werkzeug.security import generate_password_hash, check_password_hash
from src.database.database import get_db
from src.database.models import User
from sqlalchemy.orm import Session

def register_user(username, password, email=None):
    db: Session = next(get_db())
    try:
        if db.query(User).filter(User.username == username).first():
            return {"success": False, "message": "Username already exists."}
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password, email=email)
        db.add(new_user)
        db.commit()
        return {"success": True, "message": "User registered successfully."}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    finally:
        db.close()

def login_user(username, password):
    db: Session = next(get_db())
    try:
        user = db.query(User).filter(User.username == username).first()
        if user and check_password_hash(user.password_hash, password):
            return {"success": True, "user": {"id": user.id, "username": user.username}}
        return {"success": False, "message": "Invalid username or password."}
    finally:
        db.close()
