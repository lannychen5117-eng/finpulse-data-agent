import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Check for MySQL config, otherwise fall back to SQLite
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB", "finpulse")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
DB_TYPE = os.getenv("DB_TYPE", "sqlite")

if DB_TYPE == "mysql" and MYSQL_HOST:
    # 1. Connect to Server (no DB) to ensure DB exists
    server_url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}"
    engine_server = create_engine(server_url)
    try:
        with engine_server.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}"))
            print(f"Database '{MYSQL_DB}' checked/created.")
    except Exception as e:
        print(f"Warning: Could not create database (might already exist or permissions issue): {e}")

    # 2. Connect to the specific DB
    DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    print(f"Using MySQL Database: {MYSQL_HOST}/{MYSQL_DB}")
else:
    # Fallback to local SQLite
    db_path = os.path.join(os.path.dirname(__file__), '../../data/finpulse.db')
    DATABASE_URL = f"sqlite:///{db_path}"
    print(f"Using SQLite Database: {db_path}")

engine = create_engine(
    DATABASE_URL, 
    pool_recycle=3600,
    echo=False
)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    import src.database.models
    Base.metadata.create_all(bind=engine)
