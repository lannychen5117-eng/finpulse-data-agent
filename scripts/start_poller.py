#!/usr/bin/env python
"""
股票数据轮询服务启动脚本
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scheduler.stock_poller import StockPollerService

if __name__ == "__main__":
    print("=" * 60)
    print("  FinPulse 股票数据轮询服务")
    print("=" * 60)
    print()
    
    # 创建轮询服务实例
    # batch_size: 每批处理15只股票
    # interval_minutes: 每10分钟更新一次
    poller = StockPollerService(batch_size=15, interval_minutes=10)
    
    try:
        poller.start()
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"\n\n服务异常退出: {e}")
        import traceback
        traceback.print_exc()
