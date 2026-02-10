"""
多市场搜索技能 - 增强版
支持搜索股票、基金、期货，并在会话中保持搜索结果以便用户选择
"""
from langchain.tools import tool
import yfinance as yf
import akshare as ak
from typing import List, Dict, Optional

# 搜索结果缓存（用于保持上下文）
_last_search_results: List[Dict] = []

def _search_cn_funds(keyword: str) -> List[Dict]:
    """搜索中国基金"""
    results = []
    try:
        # 使用 akshare 获取基金列表
        df = ak.fund_name_em()
        if not df.empty:
            # 搜索基金代码或名称包含关键词的
            mask = df['基金代码'].str.contains(keyword) | df['基金简称'].str.contains(keyword, case=False, na=False)
            matches = df[mask].head(5)
            for _, row in matches.iterrows():
                results.append({
                    "代码": row['基金代码'],
                    "名称": row['基金简称'],
                    "市场": "A股基金"
                })
    except Exception as e:
        print(f"搜索中国基金失败: {e}")
    return results

def _search_yfinance(keyword: str) -> List[Dict]:
    """使用 yfinance 搜索"""
    results = []
    # 尝试不同的代码格式
    test_codes = [
        (keyword.upper(), "美股"),
        (f"{keyword}.SS", "A股(上海)"),
        (f"{keyword}.SZ", "A股(深圳)"),
        (f"{keyword}.HK", "港股"),
    ]
    
    for code, market in test_codes:
        try:
            ticker = yf.Ticker(code)
            info = ticker.info
            if info and info.get("regularMarketPrice"):
                name = info.get("longName", info.get("shortName", code))
                results.append({
                    "代码": code,
                    "名称": name[:30] if name else code,  # 截断过长名称
                    "市场": market
                })
        except:
            pass
    return results

# 常用产品映射
COMMON_PRODUCTS = {
    "苹果": [("AAPL", "苹果公司", "美股")],
    "茅台": [("600519.SS", "贵州茅台", "A股")],
    "腾讯": [("0700.HK", "腾讯控股", "港股"), ("TCEHY", "腾讯ADR", "美股")],
    "阿里": [("BABA", "阿里巴巴", "美股"), ("9988.HK", "阿里巴巴-W", "港股")],
    "特斯拉": [("TSLA", "特斯拉", "美股")],
    "英伟达": [("NVDA", "英伟达", "美股")],
    "微软": [("MSFT", "微软", "美股")],
    "黄金": [("GC=F", "黄金期货", "期货"), ("GLD", "黄金ETF", "美股ETF")],
    "原油": [("CL=F", "原油期货", "期货")],
    "白酒": [("512170", "招商中证白酒ETF", "A股基金"), ("161725", "招商中证白酒指数A", "A股基金"), ("012414", "招商中证白酒指数C", "A股基金")],
    "半导体": [("SMH", "半导体ETF", "美股ETF"), ("159995", "芯片ETF", "A股基金")],
    "新能源": [("516160", "新能源ETF", "A股基金")],
    "医药": [("512010", "医药ETF", "A股基金")],
    "科技": [("159941", "科技ETF", "A股基金"), ("QQQ", "纳斯达克100ETF", "美股ETF")],
}

@tool
def search_markets_tool(keyword: str) -> str:
    """
    在多个市场搜索产品（股票、基金、期货）。
    搜索后会返回编号列表，用户可以通过序号选择。
    
    Args:
        keyword: 搜索关键词（公司名、代码、基金名称等）
    """
    global _last_search_results
    results = []
    keyword_upper = keyword.upper().strip()
    
    # 1. 先检查常用映射
    for key, products in COMMON_PRODUCTS.items():
        if key in keyword or keyword in key or keyword_upper in key.upper():
            for code, name, market in products:
                results.append({"代码": code, "名称": name, "市场": market})
    
    # 2. 如果是6位数字，搜索中国基金
    if keyword.isdigit() and len(keyword) == 6:
        cn_results = _search_cn_funds(keyword)
        results.extend(cn_results)
    
    # 3. 用 yfinance 搜索
    yf_results = _search_yfinance(keyword)
    for r in yf_results:
        if not any(existing["代码"] == r["代码"] for existing in results):
            results.append(r)
    
    # 4. 如果关键词是中文，也搜索中国基金
    if any('\u4e00' <= c <= '\u9fff' for c in keyword):
        cn_results = _search_cn_funds(keyword)
        for r in cn_results:
            if not any(existing["代码"] == r["代码"] for existing in results):
                results.append(r)
    
    # 保存搜索结果到缓存
    _last_search_results = results
    
    if not results:
        return f"未找到与'{keyword}'相关的产品。请尝试使用更具体的代码或名称，例如：AAPL、600519、茅台、白酒等。"
    
    # 格式化输出
    output = f"根据关键词 **{keyword}**，找到以下 {len(results)} 个产品：\n\n"
    output += "| 序号 | 代码 | 名称 | 市场 |\n"
    output += "|------|------|------|------|\n"
    
    for i, r in enumerate(results, 1):
        output += f"| {i} | {r['代码']} | {r['名称']} | {r['市场']} |\n"
    
    output += f"\n请直接告诉我您想订阅的产品代码（如：{results[0]['代码']}），我将为您订阅。"
    
    return output

@tool
def subscribe_by_selection_tool(selection: str) -> str:
    """
    根据用户的选择（序号或代码）订阅产品。
    这个工具会自动识别用户输入的是序号还是代码。
    
    Args:
        selection: 用户选择的序号（如 "1"）或代码（如 "AAPL"）
    """
    global _last_search_results
    from src.skills.fund_skill import add_fund_tool
    
    selection = selection.strip()
    target_code = None
    target_name = None
    
    # 尝试解析为序号
    if selection.isdigit():
        idx = int(selection) - 1
        if 0 <= idx < len(_last_search_results):
            target_code = _last_search_results[idx]["代码"]
            target_name = _last_search_results[idx]["名称"]
        else:
            # 可能是基金代码
            target_code = selection
    else:
        # 直接作为代码使用
        target_code = selection.upper()
        # 查找名称
        for r in _last_search_results:
            if r["代码"].upper() == target_code:
                target_name = r["名称"]
                break
    
    if not target_code:
        return "未能识别您的选择，请提供产品代码或有效的序号。"
    
    # 调用订阅工具
    result = add_fund_tool.invoke({"ticker": target_code})
    
    if target_name:
        return f"{result}\n\n产品信息：{target_name} ({target_code})"
    return result

TOOLS = [search_markets_tool, subscribe_by_selection_tool]
