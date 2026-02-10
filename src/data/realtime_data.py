"""
实时数据获取模块
支持多数据源（akshare、新浪财经、yfinance）以分散请求压力
包含缓存机制避免频繁请求
"""
import pandas as pd
import yfinance as yf
import akshare as ak
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import requests
from functools import lru_cache

# 简单内存缓存（5分钟有效期）
_cache = {}
_cache_ttl = 300  # 5分钟

def _get_cache_key(source: str, symbol: str) -> str:
    """生成缓存键"""
    minute_bucket = datetime.now().strftime("%Y%m%d%H%M")[:11]  # 精确到10分钟
    return f"{source}_{symbol}_{minute_bucket}"

def _get_from_cache(key: str) -> Optional[Any]:
    """从缓存获取数据"""
    if key in _cache:
        data, timestamp = _cache[key]
        if (datetime.now() - timestamp).total_seconds() < _cache_ttl:
            return data
    return None

def _set_cache(key: str, data: Any):
    """设置缓存"""
    _cache[key] = (data, datetime.now())

def get_fund_realtime_data(ticker: str) -> Dict[str, Any]:
    """
    获取基金实时数据（使用 akshare）
    
    Returns:
        {
            "name": "基金名称",
            "latest_nav": 1.234,  # 最新净值
            "prev_nav": 1.200,    # 昨日净值
            "change_pct": 2.83,   # 涨跌幅%
            "update_time": "2024-05-20",
            "history": DataFrame  # 历史数据用于图表
        }
    """
    cache_key = _get_cache_key("fund", ticker)
    cached = _get_from_cache(cache_key)
    if cached:
        return cached
    
    result = {
        "name": ticker,
        "latest_nav": None,
        "prev_nav": None,
        "change_pct": None,
        "update_time": None,
        "history": pd.DataFrame()
    }
    
    try:
        # 获取基金名称
        df_name = ak.fund_name_em()
        match = df_name[df_name['基金代码'] == ticker]
        if not match.empty:
            result["name"] = match.iloc[0]['基金简称']
        
        # 获取净值历史（最近30天用于图表）
        df_nav = ak.fund_open_fund_info_em(symbol=ticker, indicator="单位净值走势")
        if not df_nav.empty and len(df_nav) >= 2:
            # 转换数据
            df_nav['净值日期'] = pd.to_datetime(df_nav['净值日期'])
            df_nav['单位净值'] = pd.to_numeric(df_nav['单位净值'])
            df_nav = df_nav.sort_values('净值日期', ascending=True)
            
            # 最新净值
            latest = df_nav.iloc[-1]
            prev = df_nav.iloc[-2]
            
            result["latest_nav"] = latest['单位净值']
            result["prev_nav"] = prev['单位净值']
            result["change_pct"] = ((latest['单位净值'] - prev['单位净值']) / prev['单位净值']) * 100
            result["update_time"] = latest['净值日期'].strftime("%Y-%m-%d")
            
            # 保留最近1个月数据用于图表
            cutoff = datetime.now() - timedelta(days=30)
            recent = df_nav[df_nav['净值日期'] >= cutoff].copy()
            recent.set_index('净值日期', inplace=True)
            result["history"] = recent
        
        _set_cache(cache_key, result)
        
    except Exception as e:
        print(f"获取基金数据失败 {ticker}: {e}")
    
    return result

def get_stock_realtime_data_sina(ticker: str) -> Optional[Dict[str, Any]]:
    """
    使用新浪财经API获取A股实时数据（分散请求压力）
    
    Args:
        ticker: A股代码（6位数字）
    """
    cache_key = _get_cache_key("sina", ticker)
    cached = _get_from_cache(cache_key)
    if cached:
        return cached
    
    try:
        # 新浪财经实时行情API
        # 沪市：sh前缀，深市：sz前缀
        prefix = "sh" if ticker.startswith(("6", "5")) else "sz"
        url = f"http://hq.sinajs.cn/list={prefix}{ticker}"
        
        response = requests.get(url, timeout=3)
        response.encoding = 'gbk'
        
        if response.status_code == 200 and response.text:
            # 解析数据
            data_str = response.text.split('"')[1]
            parts = data_str.split(',')
            
            if len(parts) > 30:
                result = {
                    "name": parts[0],
                    "price": float(parts[3]),  # 当前价
                    "prev_close": float(parts[2]),  # 昨收
                    "open": float(parts[1]),
                    "high": float(parts[4]),
                    "low": float(parts[5]),
                    "change_pct": ((float(parts[3]) - float(parts[2])) / float(parts[2])) * 100 if float(parts[2]) > 0 else 0,
                    "volume": float(parts[8]),
                    "update_time": f"{parts[30]} {parts[31]}"
                }
                
                _set_cache(cache_key, result)
                return result
                
    except Exception as e:
        print(f"新浪财经获取数据失败 {ticker}: {e}")
    
    return None

def get_stock_realtime_data(ticker: str, market: str = "AUTO") -> Dict[str, Any]:
    """
    获取股票实时数据（优先使用新浪财经，失败后使用akshare或yfinance）
    
    Args:
        ticker: 股票代码
        market: 市场类型（US, CN, HK, AUTO）
    """
    cache_key = _get_cache_key("stock", ticker)
    cached = _get_from_cache(cache_key)
    if cached:
        return cached
    
    result = {
        "name": ticker,
        "price": None,
        "change_pct": None,
        "volume": None,
        "update_time": None
    }
    
    # A股：优先使用新浪财经
    if ticker.isdigit() and len(ticker) == 6:
        sina_data = get_stock_realtime_data_sina(ticker)
        if sina_data:
            _set_cache(cache_key, sina_data)
            return sina_data
        
        # 新浪失败，尝试使用akshare
        try:
            df = ak.stock_zh_a_spot_em()
            match = df[df['代码'] == ticker]
            if not match.empty:
                row = match.iloc[0]
                result = {
                    "name": row['名称'],
                    "price": row['最新价'],
                    "change_pct": row['涨跌幅'],
                    "volume": row['成交量'],
                    "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                _set_cache(cache_key, result)
                return result
        except Exception as e:
            print(f"akshare获取A股数据失败 {ticker}: {e}")
    
    # 美股/港股：使用yfinance
    try:
        stock = yf.Ticker(ticker)
        info = stock.fast_info
        
        result = {
            "name": stock.info.get("longName", ticker),
            "price": info.last_price,
            "change_pct": ((info.last_price - info.previous_close) / info.previous_close) * 100 if info.previous_close > 0 else 0,
            "volume": info.last_volume,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        _set_cache(cache_key, result)
        
    except Exception as e:
        print(f"yfinance获取数据失败 {ticker}: {e}")
    
    return result

def get_holdings_realtime_prices(holdings: List) -> List[Dict[str, Any]]:
    """
    批量获取持仓股票的实时价格（前30只）
    
    Args:
        holdings: FundHolding 对象列表
        
    Returns:
        [
            {
                "code": "600519",
                "name": "贵州茅台",
                "weight": 10.5,
                "price": 1800.50,
                "change_pct": 2.3
            },
            ...
        ]
    """
    results = []
    
    for holding in holdings[:30]:  # 只获取前30只
        try:
            # 获取实时数据
            data = get_stock_realtime_data(holding.stock_symbol)
            
            results.append({
                "code": holding.stock_symbol,
                "name": data.get("name", holding.stock_name),
                "weight": holding.weight,
                "price": data.get("price"),
                "change_pct": data.get("change_pct")
            })
            
        except Exception as e:
            # 获取失败，使用基本信息
            print(f"获取持仓股票数据失败 {holding.stock_symbol}: {e}")
            results.append({
                "code": holding.stock_symbol,
                "name": holding.stock_name,
                "weight": holding.weight,
                "price": None,
                "change_pct": None
            })
    
    return results

def analyze_trend_24h(history_df: pd.DataFrame) -> str:
    """
    分析24h走势
    
    Returns:
        趋势描述，例如: "强势上涨 🚀 | RSI: 72.3"
    """
    if history_df.empty or len(history_df) < 2:
        return "数据不足"
    
    try:
        # 计算涨跌幅
        first_price = history_df.iloc[0]['单位净值'] if '单位净值' in history_df.columns else history_df.iloc[0]['Close']
        last_price = history_df.iloc[-1]['单位净值'] if '单位净值' in history_df.columns else history_df.iloc[-1]['Close']
        
        change_pct = ((last_price - first_price) / first_price) * 100
        
        # 趋势判断
        if change_pct > 2:
            trend = "强势上涨 🚀"
        elif change_pct > 0.5:
            trend = "小幅上涨 📈"
        elif change_pct > -0.5:
            trend = "横盘震荡 ➡️"
        elif change_pct > -2:
            trend = "小幅下跌 📉"
        else:
            trend = "大幅下跌 💥"
        
        return f"{trend} ({change_pct:+.2f}%)"
        
    except Exception as e:
        print(f"分析走势失败: {e}")
        return "分析失败"

def clear_cache():
    """
    清除所有缓存数据，用于手动刷新
    """
    global _cache
    _cache = {}
    print("缓存已清除")

def get_holdings_prices_from_db(db, holdings: List) -> List[Dict[str, Any]]:
    """
    从数据库获取持仓股票价格（替代实时API调用）
    
    Args:
        db: 数据库会话
        holdings: FundHolding 对象列表
        
    Returns:
        持仓股票数据列表（含贡献度）
    """
    from src.services.stock_quote_service import StockQuoteService
    
    symbols = [h.stock_symbol for h in holdings[:30]]
    quotes_map = {q['code']: q for q in StockQuoteService.get_batch_quotes(db, symbols)}
    
    results = []
    for holding in holdings[:30]:
        quote = quotes_map.get(holding.stock_symbol, {})
        
        change_pct = quote.get("change_pct", 0) or 0
        contribution = holding.weight * change_pct / 100 if change_pct else 0
        
        results.append({
            "code": holding.stock_symbol,
            "name": quote.get("name", holding.stock_name),
            "weight": holding.weight,
            "price": quote.get("price"),
            "change_pct": change_pct,
            "贡献度": contribution
        })
    
    return results
