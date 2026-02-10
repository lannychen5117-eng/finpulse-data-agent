"""
股票数据轮询服务
定期从外部API获取股票数据并存入数据库
"""
import time
import random
import schedule
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.database.models import FundHolding, StockQuote, MarketType
import akshare as ak

class StockPollerService:
    def __init__(self, batch_size=15, interval_minutes=10):
        """
        初始化轮询服务
        
        Args:
            batch_size: 每批处理的股票数量
            interval_minutes: 轮询间隔（分钟）
        """
        self.batch_size = batch_size
        self.interval_minutes = interval_minutes
    
    def is_trading_time(self) -> bool:
        """
        判断当前是否为A股交易时间
        
        交易时间:
        - 周一至周五
        - 9:30-11:30 (上午)
        - 13:00-15:00 (下午)
        
        Returns:
            bool: 是否在交易时间内
        """
        now = datetime.now()
        
        # 检查是否为交易日（周一到周五）
        if now.weekday() >= 5:  # 周六、周日
            return False
        
        # 检查是否在交易时间段
        hour = now.hour
        minute = now.minute
        
        # 上午: 9:30-11:30
        is_morning = (hour == 9 and minute >= 30) or (10 <= hour < 11) or (hour == 11 and minute <= 30)
        
        # 下午: 13:00-15:00
        is_afternoon = 13 <= hour < 15
        
        return is_morning or is_afternoon
    
    def get_all_symbols_to_update(self, db: Session):
        """获取所有需要更新的股票代码（从FundHolding表）"""
        symbols = db.query(FundHolding.stock_symbol).distinct().all()
        return [s[0] for s in symbols if s[0]]  # 过滤空值
    
    def fetch_stock_data_east_money(self, symbol: str):
        """
        使用东方财富接口获取A股数据（akshare稳定版）
        
        Args:
            symbol: 股票代码（6位数字）
            
        Returns:
            dict: 股票数据，失败返回None
        """
        try:
            # 东方财富接口：比新浪稳定
            df = ak.stock_zh_a_spot_em()
            match = df[df['代码'] == symbol]
            
            if not match.empty:
                row = match.iloc[0]
                return {
                    "name": row['名称'],
                    "price": float(row['最新价']),
                    "prev_close": float(row['昨收']),
                    "change_pct": float(row['涨跌幅']),
                    "volume": float(row['成交量']),
                    "high": float(row['最高']),
                    "low": float(row['最低']),
                    "data_source": "east_money"
                }
        except Exception as e:
            print(f"东方财富接口获取 {symbol} 失败: {e}")
        
        return None
    
    def update_stock_batch(self, db: Session, symbols: list):
        """
        批量更新股票数据（优化版：防反爬）
        
        Args:
            db: 数据库会话
            symbols: 股票代码列表
            
        Returns:
            tuple: (成功数, 失败数)
        """
        success_count = 0
        fail_count = 0
        
        for symbol in symbols:
            try:
                # A股：使用东方财富接口（优先）
                if symbol.isdigit() and len(symbol) == 6:
                    data = self.fetch_stock_data_east_money(symbol)
                    
                    if data:
                        # 更新或插入
                        quote = db.query(StockQuote).filter(
                            StockQuote.symbol == symbol
                        ).first()
                        
                        if quote:
                            # 更新
                            quote.name = data['name']
                            quote.price = data['price']
                            quote.prev_close = data['prev_close']
                            quote.change_pct = data['change_pct']
                            quote.volume = data['volume']
                            quote.high = data['high']
                            quote.low = data['low']
                            quote.data_source = data['data_source']
                            quote.updated_at = datetime.utcnow()
                        else:
                            # 插入
                            quote = StockQuote(
                                symbol=symbol,
                                name=data['name'],
                                price=data['price'],
                                prev_close=data['prev_close'],
                                change_pct=data['change_pct'],
                                volume=data['volume'],
                                high=data['high'],
                                low=data['low'],
                                market_type=MarketType.CN_STOCK,
                                data_source=data['data_source']
                            )
                            db.add(quote)
                        
                        success_count += 1
                
                # 防反爬：随机延迟1-3秒
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"更新股票 {symbol} 失败: {e}")
                fail_count += 1
        
        db.commit()
        return success_count, fail_count
    
    def poll_task(self):
        """轮询任务主逻辑"""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now_str}] 检查是否为交易时间...")
        
        # 检查交易时间
        if not self.is_trading_time():
            print("❌ 当前不在交易时间（周一至周五 9:30-11:30, 13:00-15:00），跳过轮询")
            return
        
        print("✅ 当前为交易时间，开始股票数据轮询...")
        
        db = next(get_db())
        
        try:
            # 获取所有股票
            symbols = self.get_all_symbols_to_update(db)
            print(f"需要更新的股票: {len(symbols)} 只")
            
            if len(symbols) == 0:
                print("无需更新的股票")
                return
            
            # 分批处理
            total_success = 0
            total_fail = 0
            
            for i in range(0, len(symbols), self.batch_size):
                batch = symbols[i:i + self.batch_size]
                print(f"处理批次 {i//self.batch_size + 1}: {len(batch)} 只股票")
                
                success, fail = self.update_stock_batch(db, batch)
                total_success += success
                total_fail += fail
                
                # 批次间延迟2-4秒（防反爬）
                if i + self.batch_size < len(symbols):
                    delay = random.uniform(2, 4)
                    print(f"批次延迟 {delay:.1f} 秒...")
                    time.sleep(delay)
            
            print(f"轮询完成: 成功 {total_success}, 失败 {total_fail}")
            
        except Exception as e:
            print(f"轮询任务异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
    
    def start(self):
        """启动调度器"""
        print(f"股票轮询服务启动中...")
        
        # 立即执行一次
        self.poll_task()
        
        # 定时执行
        schedule.every(self.interval_minutes).minutes.do(self.poll_task)
        
        print(f"股票轮询服务已启动，每 {self.interval_minutes} 分钟更新一次")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
