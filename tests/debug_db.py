import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")

print(f"Connecting to {MYSQL_HOST} as {MYSQL_USER}...")

# URL without database
url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}"

try:
    engine = create_engine(url)
    with engine.connect() as conn:
        print("Successfully connected to MySQL server!")
        
        # Try to list databases
        try:
            result = conn.execute(text("SHOW DATABASES;"))
            dbs = [row[0] for row in result]
            print("Available Databases:", dbs)
        except Exception as e:
            print(f"Could not list databases: {e}")
            
        # Try to create 'finpulse'
        try:
            conn.execute(text("CREATE DATABASE IF NOT EXISTS finpulse;"))
            print("Successfully executed CREATE DATABASE finpulse.")
        except Exception as e:
            print(f"Failed to create database 'finpulse': {e}")
            
except Exception as e:
    print(f"Failed to connect to server: {e}")
