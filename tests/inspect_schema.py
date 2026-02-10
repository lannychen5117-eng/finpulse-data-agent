import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")

print(f"Connecting to {MYSQL_HOST}/{MYSQL_DB}...")
url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
engine = create_engine(url)

try:
    with engine.connect() as conn:
        inspector = inspect(engine)
        if inspector.has_table("users"):
            print("Table 'users' exists.")
            indexes = inspector.get_indexes("users")
            for idx in indexes:
                print(f"Index: {idx['name']}, Unique: {idx['unique']}, Columns: {idx['column_names']}")
            
except Exception as e:
    print(f"Error: {e}")
