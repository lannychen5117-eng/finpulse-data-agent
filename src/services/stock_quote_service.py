"""
股票行情数据访问服务
从数据库读取股票实时数据
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.models import StockQuote

class StockQuoteService:
    @staticmethod
    def get_quote(db: Session, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取单只股票行情
        
        Args:
            db: 数据库会话
            symbol: 股票代码
            
        Returns:
            股票数据字典，不存在返回None
        """
        quote = db.query(StockQuote).filter(StockQuote.symbol == symbol).first()
        
        if not quote:
            return None
        
        # 计算数据年龄（分钟）
        data_age = int((datetime.utcnow() - quote.updated_at).total_seconds() / 60)
        
        return {
            "name": quote.name,
            "price": quote.price,
            "change_pct": quote.change_pct,
            "volume": quote.volume,
            "high": quote.high,
            "low": quote.low,
            "update_time": quote.updated_at.strftime("%Y-%m-%d %H:%M"),
            "data_age_minutes": data_age
        }
    
    @staticmethod
    def get_batch_quotes(db: Session, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        批量获取股票行情（从数据库）
        
        Args:
            db: 数据库会话
            symbols: 股票代码列表
            
        Returns:
            股票数据列表
        """
        quotes = db.query(StockQuote).filter(StockQuote.symbol.in_(symbols)).all()
        
        results = []
        for quote in quotes:
            results.append({
                "code": quote.symbol,
                "name": quote.name,
                "price": quote.price,
                "change_pct": quote.change_pct,
                "volume": quote.volume,
                "update_time": quote.updated_at.strftime("%Y-%m-%d %H:%M")
            })
        
        return results
    
    @staticmethod
    def is_data_fresh(db: Session, max_age_minutes=15) -> bool:
        """
        检查数据是否新鲜
        
        Args:
            db: 数据库会话
            max_age_minutes: 最大年龄（分钟）
            
        Returns:
            是否新鲜
        """
        latest = db.query(StockQuote).order_by(StockQuote.updated_at.desc()).first()
        
        if not latest:
            return False
        
        age = (datetime.utcnow() - latest.updated_at).total_seconds() / 60
        return age <= max_age_minutes
    
    @staticmethod
    def get_data_stats(db: Session) -> Dict[str, Any]:
        """
        获取数据统计信息
        
        Returns:
            统计数据字典
        """
        total_count = db.query(StockQuote).count()
        
        if total_count == 0:
            return {
                "total_stocks": 0,
                "latest_update": None,
                "oldest_update": None,
                "is_fresh": False
            }
        
        latest = db.query(StockQuote).order_by(StockQuote.updated_at.desc()).first()
        oldest = db.query(StockQuote).order_by(StockQuote.updated_at.asc()).first()
        
        return {
            "total_stocks": total_count,
            "latest_update": latest.updated_at.strftime("%Y-%m-%d %H:%M"),
            "oldest_update": oldest.updated_at.strftime("%Y-%m-%d %H:%M"),
            "is_fresh": StockQuoteService.is_data_fresh(db)
        }
