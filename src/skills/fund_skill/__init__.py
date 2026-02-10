from langchain.tools import tool
from typing import Optional
from datetime import datetime
from src.database.database import get_db
from src.database.models import Subscription, FundHolding, MarketType
from src.data.fund import analyze_fund
from src.data.fund_loader import get_fund_holdings, get_fund_info
from src.agent.user_context import get_current_user_id
from src.utils.viz_utils import VizUtils

viz = VizUtils()

def _guess_market_type(ticker: str) -> MarketType:
    """Guess market type based on ticker format."""
    ticker = ticker.upper()
    if ".HK" in ticker:
        return MarketType.HK_STOCK
    elif ".SS" in ticker or ".SZ" in ticker:
        return MarketType.CN_STOCK
    elif ticker.isdigit() and len(ticker) == 6:
        return MarketType.FUND
    elif "=" in ticker:
        return MarketType.FUTURE
    else:
        return MarketType.US_STOCK

def _store_fund_holdings(subscription_id: int, ticker: str, db):
    """Fetch and store fund holdings for a subscription."""
    holdings = get_fund_holdings(ticker)
    if holdings:
        for h in holdings:
            holding = FundHolding(
                subscription_id=subscription_id,
                stock_symbol=h.get("symbol", ""),
                stock_name=h.get("name", ""),
                weight=h.get("weight", 0.0),
                updated_at=datetime.utcnow()
            )
            db.add(holding)
        db.commit()
        return len(holdings)
    return 0

@tool
def add_fund_tool(ticker: str, market: str = "AUTO") -> str:
    """
    Subscribe to a fund, stock, or futures for monitoring.
    Args:
        ticker: The symbol to subscribe (e.g., AAPL, 000001, 2800.HK, GC=F)
        market: Market type hint - US, CN, HK, FUTURE, or AUTO (auto-detect)
    
    Note: User must be logged in. Subscriptions are user-specific.
    """
    user_id = get_current_user_id()
    print(f"[DEBUG add_fund_tool] ticker={ticker}, user_id={user_id}")
    
    if not user_id:
        return "请先登录后再订阅。(Please login first.)"
    
    try:
        db = next(get_db())
        ticker = ticker.upper().strip()
        
        # Check if already subscribed by this user
        existing = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.symbol == ticker
        ).first()
        
        if existing:
            db.close()
            return f"您已订阅 {ticker}。(Already subscribed.)"
        
        # Determine market type
        if market.upper() == "AUTO":
            market_type = _guess_market_type(ticker)
        else:
            market_map = {
                "US": MarketType.US_STOCK,
                "CN": MarketType.CN_STOCK,
                "HK": MarketType.HK_STOCK,
                "FUND": MarketType.FUND,
                "FUTURE": MarketType.FUTURE
            }
            market_type = market_map.get(market.upper(), MarketType.US_STOCK)
        
        # Get fund/stock info for notes
        info = get_fund_info(ticker)
        print(f"[DEBUG add_fund_tool] info={info}, market_type={market_type}")
        
        # Create subscription
        sub = Subscription(
            user_id=user_id,
            symbol=ticker,
            market_type=market_type,
            notes=info.get("name", ticker)
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        print(f"[DEBUG add_fund_tool] Created subscription id={sub.id}")
        
        # If it's a fund/ETF, fetch and store holdings
        holdings_count = 0
        if market_type in [MarketType.FUND, MarketType.US_STOCK]:
            holdings_count = _store_fund_holdings(sub.id, ticker, db)
        
        db.close()
        
        result = f"✅ 成功订阅 {ticker} ({info.get('name', ticker)})！\n"
        result += f"市场类型: {market_type.value}\n"
        if holdings_count > 0:
            result += f"已获取 {holdings_count} 只成分股信息。\n"
        result += "您可以在监控看板中查看实时数据。"
        return result
        
    except Exception as e:
        import traceback
        print(f"[DEBUG add_fund_tool] Exception: {e}")
        print(traceback.format_exc())
        return f"订阅失败: {e}"

@tool
def remove_fund_tool(ticker: str) -> str:
    """
    Unsubscribe from a fund or stock.
    """
    user_id = get_current_user_id()
    if not user_id:
        return "请先登录后再操作。"
    
    try:
        db = next(get_db())
        ticker = ticker.upper().strip()
        sub = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.symbol == ticker
        ).first()
        
        if sub:
            db.delete(sub)  # Also deletes holdings due to cascade
            db.commit()
            db.close()
            return f"✅ 已取消订阅 {ticker}。"
        db.close()
        return f"{ticker} 未在您的订阅列表中。"
    except Exception as e:
        return f"取消订阅失败: {e}"

@tool
def list_funds_tool() -> str:
    """
    List all your subscribed funds/stocks.
    """
    user_id = get_current_user_id()
    if not user_id:
        return "请先登录。"
    
    try:
        db = next(get_db())
        subs = db.query(Subscription).filter(Subscription.user_id == user_id).all()
        db.close()
        
        if not subs:
            return "您尚未订阅任何产品。使用 '订阅 + 代码' 来添加。"
        
        result = "📋 您的订阅列表:\n"
        for s in subs:
            result += f"• {s.symbol} ({s.market_type.value}) - {s.notes or ''}\n"
        return result
    except Exception as e:
        return f"获取订阅列表失败: {e}"

@tool
def analyze_funds_tool() -> str:
    """
    Analyze all your subscribed funds and generate a report.
    """
    user_id = get_current_user_id()
    if not user_id:
        return "请先登录。"
    
    try:
        db = next(get_db())
        subs = db.query(Subscription).filter(Subscription.user_id == user_id).all()
        db.close()
        
        if not subs:
            return "您尚未订阅任何产品。请先订阅后再分析。"
        
        report = ["📊 订阅产品分析报告", "=" * 30]
        for sub in subs:
            result = analyze_fund(sub.symbol)
            if "error" in result:
                report.append(f"❌ {sub.symbol}: {result['error']}")
                continue
            
            emoji = "🟢" if result['recommendation'] == "BUY" else ("🔴" if result['recommendation'] == "SELL" else "🟡")
            report.append(f"\n{emoji} **{result['ticker']}** ({sub.notes or ''})")
            report.append(f"  价格: {result['price']:.2f}")
            report.append(f"  RSI: {result['rsi']:.2f}")
            report.append(f"  MACD: {result['macd']:.2f}")
            report.append(f"  建议: {result['recommendation']}")
            report.append(f"  原因: {result['reason']}")
        
        return "\n".join(report)
    except Exception as e:
        return f"分析失败: {e}"

@tool
def analyze_fund_tool(ticker: str) -> str:
    """
    Analyze a specific fund or stock (no subscription required).
    """
    result = analyze_fund(ticker)
    if "error" in result:
        return f"分析失败: {result['error']}"
    
    emoji = "🟢" if result['recommendation'] == "BUY" else ("🔴" if result['recommendation'] == "SELL" else "🟡")
    return (f"{emoji} **{result['ticker']}** 分析结果:\n"
            f"价格: {result['price']:.2f}\n"
            f"RSI: {result['rsi']:.2f}\n"
            f"MACD: {result['macd']:.2f}\n"
            f"建议: {result['recommendation']}\n"
            f"原因: {result['reason']}")

TOOLS = [
    add_fund_tool,
    remove_fund_tool,
    list_funds_tool,
    analyze_funds_tool,
    analyze_fund_tool
]
