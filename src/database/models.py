from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from src.database.database import Base

class MarketType(enum.Enum):
    US_STOCK = "US_STOCK"
    CN_STOCK = "CN_STOCK"
    HK_STOCK = "HK_STOCK"
    FUND = "FUND"
    FUTURE = "FUTURE"
    CRYPTO = "CRYPTO"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscriptions = relationship("Subscription", back_populates="user")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String(20), index=True, nullable=False)
    market_type = Column(Enum(MarketType), default=MarketType.US_STOCK)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="subscriptions")
    holdings = relationship("FundHolding", back_populates="subscription", cascade="all, delete-orphan")

class FundHolding(Base):
    """Stores holdings (composition) for fund/ETF subscriptions."""
    __tablename__ = "fund_holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    stock_symbol = Column(String(20), index=True, nullable=False)
    stock_name = Column(String(100), nullable=True)
    weight = Column(Float, nullable=True)  # Percentage weight in the fund
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    subscription = relationship("Subscription", back_populates="holdings")

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True, nullable=False)
    price = Column(Float, nullable=False)
    change_percent = Column(Float, nullable=True)
    volume = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class StockQuote(Base):
    """股票实时行情（持久化存储）"""
    __tablename__ = "stock_quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True, nullable=False, unique=True)
    name = Column(String(100), nullable=True)
    price = Column(Float, nullable=True)
    prev_close = Column(Float, nullable=True)
    change_pct = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    market_type = Column(Enum(MarketType), default=MarketType.CN_STOCK)
    data_source = Column(String(20), nullable=True)  # sina/akshare/yfinance
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
