import yfinance as yf
import pandas as pd
import akshare as ak
from typing import Dict, Any, Optional
import datetime

def is_cn_fund(ticker: str) -> bool:
    """
    Check if the ticker looks like a Chinese fund code (6 digits).
    Stock codes also have 6 digits, but usually funds are passed as just 6 digits in this context.
    """
    return len(ticker) == 6 and ticker.isdigit()

def get_fund_history(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """
    Fetch fund history. 
    If it's a 6-digit code, try akshare for Chinese open-ended funds.
    Otherwise fall back to yfinance.
    
    Returns a DataFrame with columns: Open, High, Low, Close, Volume.
    For funds, O/H/L/C might be the same (Net Value).
    """
    if is_cn_fund(ticker):
        try:
            # akshare: fund_open_fund_info_em is good for net value history
            # Returns columns like: '净值日期', '单位净值', '日增长率', ...
            df = ak.fund_open_fund_info_em(symbol=ticker, indicator="单位净值走势")
            
            if df.empty:
                 return pd.DataFrame()
                 
            # Rename columns
            # '净值日期' -> Date (index)
            # '单位净值' -> Close
            df['Date'] = pd.to_datetime(df['净值日期'])
            df.set_index('Date', inplace=True)
            df['Close'] = pd.to_numeric(df['单位净值'])
            
            # For funds, we might not have High/Low/Open, so fill with Close
            df['Open'] = df['Close']
            df['High'] = df['Close']
            df['Low'] = df['Close']
            df['Volume'] = 0 
            
            # Filter by period (approximate)
            end_date = datetime.datetime.now()
            if period == "1mo":
                start_date = end_date - datetime.timedelta(days=30)
            elif period == "3mo":
                start_date = end_date - datetime.timedelta(days=90)
            elif period == "6mo":
                start_date = end_date - datetime.timedelta(days=180)
            elif period == "1y":
                start_date = end_date - datetime.timedelta(days=365)
            else: # Max or others, default to 1y to be safe or just return all
                start_date = end_date - datetime.timedelta(days=365)
                
            # Ensure index is sorted
            df.sort_index(inplace=True)
            
            mask = (df.index >= start_date) & (df.index <= end_date)
            df_filtered = df.loc[mask].copy()
            
            return df_filtered[['Open', 'High', 'Low', 'Close', 'Volume']]
            
        except Exception as e:
            print(f"Error fetching data from akshare for {ticker}: {e}")
            return pd.DataFrame()
            
    else:
        # Use yfinance
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            return df
        except Exception as e:
            print(f"Error fetching data from yfinance for {ticker}: {e}")
            return pd.DataFrame()

def get_fund_info(ticker: str) -> Dict[str, Any]:
    """
    Get basic fund/stock info.
    """
    info = {"ticker": ticker, "name": ticker, "type": "Unknown"}
    
    if is_cn_fund(ticker):
        info["type"] = "CN Fund"
        try:
            # Use akshare to get fund name
            df = ak.fund_name_em()
            match = df[df['基金代码'] == ticker]
            if not match.empty:
                info["name"] = match.iloc[0]['基金简称']
        except Exception as e:
            print(f"Error fetching CN fund info for {ticker}: {e}")
    else:
        try:
             stock = yf.Ticker(ticker)
             y_info = stock.info
             info["name"] = y_info.get("longName", ticker)
             info["type"] = y_info.get("quoteType", "Stock")
        except:
             pass
             
    return info

def get_fund_holdings(ticker: str) -> list:
    """
    Get fund/ETF holdings (top stocks in the fund).
    Returns a list of dicts with keys: symbol, name, weight.
    
    For US ETFs: Uses yfinance.
    For CN Funds: Uses akshare (if available).
    """
    holdings = []
    
    if is_cn_fund(ticker):
        try:
            # akshare: fund_portfolio_hold_em for CN fund holdings
            df = ak.fund_portfolio_hold_em(symbol=ticker, date="2024")
            if not df.empty:
                # Columns: '序号', '股票代码', '股票名称', '占净值比例', '持仓市值', '季度'
                for _, row in df.head(20).iterrows():  # Top 20 holdings
                    holdings.append({
                        "symbol": str(row.get('股票代码', '')),
                        "name": str(row.get('股票名称', '')),
                        "weight": float(row.get('占净值比例', 0)) if row.get('占净值比例') else 0.0
                    })
        except Exception as e:
            print(f"Error fetching CN fund holdings for {ticker}: {e}")
    else:
        try:
            # yfinance: ETF Holders (for US ETFs like SPY, QQQ)
            stock = yf.Ticker(ticker)
            # Different yfinance versions might have different API
            # Some have .institutional_holders, some have .major_holders
            # For ETFs, we can try to get the top holdings
            if hasattr(stock, 'major_holders'):
                # This doesn't give individual stocks, so we try another approach
                pass
            
            # Try to get fund info which sometimes has holdings
            info = stock.info
            if info.get("quoteType") == "ETF":
                # For ETFs, yfinance doesn't directly provide holdings
                # We can use a workaround or note this limitation
                # For now, return empty and log
                print(f"Note: ETF holdings for {ticker} require premium data source")
            
        except Exception as e:
            print(f"Error fetching holdings for {ticker}: {e}")
    
    return holdings

