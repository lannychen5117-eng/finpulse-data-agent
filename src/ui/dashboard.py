"""
Dashboard UI - 监控看板
显示实时市场数据、用户订阅的基金/股票信息
"""
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import time

from src.database.database import get_db
from src.database.models import Subscription, MarketType
from src.ui.charts import render_candlestick_chart
from src.data.stock import get_stock_history
from src.analysis.technical import add_technical_indicators
from src.data.realtime_data import (
    get_fund_realtime_data,
    get_stock_realtime_data,
    get_holdings_prices_from_db,
    analyze_trend_24h,
    clear_cache
)

def get_market_indices_with_history():
    """Fetch major market indices with recent history for sparklines."""
    tickers = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Shanghai": "000001.SS",
        "Gold": "GC=F",
        "Oil": "CL=F"
    }
    
    indices_data = []
    
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if not hist.empty:
                latest = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) > 1 else latest
                change_pct = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
                
                indices_data.append({
                    "Name": name,
                    "Symbol": symbol,
                    "Current": latest['Close'],
                    "Change": change_pct,
                    "History": hist
                })
        except Exception as e:
            print(f"Error fetching {name}: {e}")
            
    return indices_data

def render_dashboard():
    st.header("Global Market Overview 🌍")
    
    # 1. Market Indices with Sparklines
    with st.spinner("Fetching market data..."):
        indices = get_market_indices_with_history()
        
    if indices:
        cols = st.columns(len(indices))
        for i, data in enumerate(indices):
            with cols[i]:
                fig = go.Figure()
                color = "green" if data['Change'] >= 0 else "red"
                
                fig.add_trace(go.Scatter(
                    x=data['History'].index, 
                    y=data['History']['Close'],
                    mode='lines',
                    line=dict(color=color, width=2),
                    fill='tozeroy',
                    fillcolor=f'rgba({200 if color=="red" else 0},{200 if color=="green" else 0},0,0.1)'
                ))
                
                fig.update_layout(
                    showlegend=False,
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=60,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.metric(
                    label=data['Name'],
                    value=f"{data['Current']:,.2f}",
                    delta=f"{data['Change']:.2f}%"
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("Failed to fetch market data.")
        
    st.divider()
    
    # 2. User Subscriptions with Refresh Controls
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.subheader("我的订阅监控 📋")
    with col2:
        if st.button("🔄 刷新数据", key="refresh_btn", use_container_width=True):
            clear_cache()
            st.rerun()
    with col3:
        auto_refresh = st.toggle("⚡ 自动刷新", key="auto_refresh", value=False)
    
    # Display last update time and auto-refresh info
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.caption(f"💡 数据可能延迟15分钟 | 最后更新: {datetime.now().strftime('%H:%M:%S')}")
    with col_b:
        if auto_refresh:
            st.caption("⏱️ 将在30秒后自动刷新")
    
    if "user" not in st.session_state:
        st.warning("请先登录查看您的订阅。")
        return

    db = next(get_db())
    user_id = st.session_state["user"]["id"]
    subs = db.query(Subscription).filter(Subscription.user_id == user_id).all()
    
    if not subs:
        st.info("您尚未订阅任何产品。在对话中输入 '订阅 AAPL' 来添加！")
        db.close()
        return
    
    # Create enhanced subscription table
    st.markdown("### 实时行情")
    
    # Table header 
    cols = st.columns([3, 2, 2, 2, 2, 3])
    cols[0].markdown("**名称**")
    cols[1].markdown("**代码**")
    cols[2].markdown("**最新价/净值**") 
    cols[3].markdown("**涨跌%**")
    cols[4].markdown("**类型**")
    cols[5].markdown("**24h走势**")
    
    for sub in subs:
        cols = st.columns([3, 2, 2, 2, 2, 3])
        
        try:
            # 判断是基金还是股票
            is_fund = sub.market_type in [MarketType.FUND, MarketType.CN_STOCK] and sub.symbol.isdigit() and len(sub.symbol) == 6
            
            if is_fund:
                # 获取基金实时数据
                data = get_fund_realtime_data(sub.symbol)
                name = data.get("name", sub.symbol)
                price = data.get("latest_nav")
                change_pct = data.get("change_pct")
                history = data.get("history", pd.DataFrame())
            else:
                # 获取股票实时数据
                data = get_stock_realtime_data(sub.symbol)
                name = data.get("name", sub.notes or sub.symbol)
                price = data.get("price")
                change_pct = data.get("change_pct")
                # 获取历史数据用于图表
                history = get_stock_history(sub.symbol, period="1d")
                if history.empty:
                    history = get_stock_history(sub.symbol, period="5d")
            
            # Display data
            if price is not None and change_pct is not None:
                emoji = "🟢" if change_pct >= 0 else "🔴"
                
                cols[0].markdown(f"**{name}**")
                cols[1].markdown(f"`{sub.symbol}`")
                cols[2].markdown(f"{'¥' if is_fund else '$'}{price:.3f}" if is_fund else f"${price:.2f}")
                cols[3].markdown(f"{emoji} {change_pct:+.2f}%")
                cols[4].markdown(f"{sub.market_type.value}")
                
                # Mini sparkline
                if not history.empty:
                    fig = go.Figure()
                    color = "green" if change_pct >= 0 else "red"
                    
                    y_data = history['单位净值'].values if '单位净值' in history.columns else history['Close'].values
                    
                    fig.add_trace(go.Scatter(
                        x=list(range(len(history))),
                        y=y_data,
                        mode='lines',
                        line=dict(color=color, width=1.5),
                        fill='tozeroy',
                        fillcolor=f'rgba({200 if color=="red" else 0},{200 if color=="green" else 0},0,0.1)'
                    ))
                    fig.update_layout(
                        showlegend=False,
                        xaxis=dict(visible=False),
                        yaxis=dict(visible=False),
                        margin=dict(l=0, r=0, t=0, b=0),
                        height=40,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    cols[5].plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else:
                    cols[5].markdown("--")
            else:
                cols[0].markdown(f"**{sub.notes or sub.symbol}**")
                cols[1].markdown(f"`{sub.symbol}`")
                cols[2].markdown("--")
                cols[3].markdown("--")
                cols[4].markdown(f"{sub.market_type.value}")
                cols[5].markdown("数据获取中...")
                
        except Exception as e:
            print(f"Error displaying {sub.symbol}: {e}")
            cols[0].markdown(f"**{sub.notes or sub.symbol}**")
            cols[1].markdown(f"`{sub.symbol}`")
            cols[2].markdown("错误")
            cols[3].markdown("--")
            cols[4].markdown(f"{sub.market_type.value}")
            cols[5].markdown("❌")
    
    st.divider()
    
    # 3. Detailed Analysis Section
    st.subheader("详细分析")
    selected = st.selectbox(
        "选择产品查看详细分析", 
        [s.symbol for s in subs],
        format_func=lambda x: f"{x} - {next((s.notes for s in subs if s.symbol == x), x)}"
    )
    
    if selected:
        with st.spinner(f"加载 {selected} 详细数据..."):
            # 获取选中的订阅信息
            sub = next((s for s in subs if s.symbol == selected), None)
            if not sub:
                db.close()
                return
            
            is_fund = sub.market_type in [MarketType.FUND, MarketType.CN_STOCK] and sub.symbol.isdigit() and len(sub.symbol) == 6
            
            if is_fund:
                # ========== 基金详细分析 ==========
                fund_data = get_fund_realtime_data(selected)
                
                # 基金信息卡片
                st.markdown("#### 📊 基金概况")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        label="基金名称",
                        value=fund_data.get("name", selected)
                    )
                
                with col2:
                    st.metric(
                        label="最新净值",
                        value=f"¥{fund_data.get('latest_nav', 0):.4f}",
                        delta=f"{fund_data.get('change_pct', 0):+.2f}%"
                    )
                
                with col3:
                    st.metric(
                        label="昨日净值",
                        value=f"¥{fund_data.get('prev_nav', 0):.4f}"
                    )
                
                with col4:
                    trend = analyze_trend_24h(fund_data.get("history", pd.DataFrame()))
                    st.metric(
                        label="走势研判",
                        value=trend
                    )
                
                # 净值走势图
                st.markdown("#### 📈 净值走势（30天）")
                history = fund_data.get("history", pd.DataFrame())
                if not history.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=history.index,
                        y=history['单位净值'],
                        mode='lines+markers',
                        name='单位净值',
                        line=dict(color='#1f77b4', width=2),
                        marker=dict(size=4)
                    ))
                    fig.update_layout(
                        title="",
                        xaxis_title="日期",
                        yaxis_title="净值（元）",
                        hovermode='x unified',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无历史净值数据")
                
                # 持仓股票分析（前30只）
                if sub.holdings:
                    st.markdown("#### 🏢 前30大持仓股票")
                    
                    # 检查数据新鲜度
                    from src.services.stock_quote_service import StockQuoteService
                    is_fresh = StockQuoteService.is_data_fresh(db, max_age_minutes=15)
                    
                    col_status, col_count = st.columns([3, 1])
                    with col_status:
                        if is_fresh:
                            st.success("✅ 数据新鲜（15分钟内）")
                        else:
                            st.warning("⚠️ 数据可能过时，后台正在更新...")
                    with col_count:
                        st.caption(f"共 {len(sub.holdings)} 只股票 | 显示前30")
                    
                    with st.spinner("获取持仓股票实时价格..."):
                        holdings_data = get_holdings_prices_from_db(db, sub.holdings)
                    
                    if holdings_data:
                        # 创建DataFrame
                        df_holdings = pd.DataFrame(holdings_data)
                        
                        # 计算贡献度（简化版：权重 * 涨跌幅）
                        df_holdings['贡献度'] = df_holdings.apply(
                            lambda row: row['weight'] * row['change_pct'] / 100 if row['change_pct'] is not None else 0,
                            axis=1
                        )
                        
                        # 格式化显示
                        df_display = df_holdings.copy()
                        df_display['序号'] = range(1, len(df_display) + 1)
                        df_display['权重%'] = df_display['weight'].apply(lambda x: f"{x:.2f}%")
                        df_display['最新价'] = df_display['price'].apply(lambda x: f"¥{x:.2f}" if x else "--")
                        df_display['涨跌%'] = df_display['change_pct'].apply(
                            lambda x: f"{'🟢' if x >= 0 else '🔴'} {x:+.2f}%" if x is not None else "--"
                        )
                        df_display['贡献度'] = df_display['贡献度'].apply(lambda x: f"{x:+.4f}%")
                        
                        # 选择要显示的列
                        df_final = df_display[['序号', 'code', 'name', '权重%', '最新价', '涨跌%', '贡献度']]
                        df_final.columns = ['序号', '股票代码', '股票名称', '权重%', '最新价', '涨跌%', '贡献度']
                        
                        st.dataframe(
                            df_final,
                            width=None,
                            hide_index=True,
                            height=600
                        )
                        
                        # 持仓涨跌分布
                        st.markdown("#### 📊 持仓涨跌分布")
                        valid_changes = [h['change_pct'] for h in holdings_data if h['change_pct'] is not None]
                        
                        if valid_changes:
                            up_count = sum(1 for x in valid_changes if x > 0)
                            down_count = sum(1 for x in valid_changes if x < 0)
                            flat_count = sum(1 for x in valid_changes if x == 0)
                            
                            col1, col2, col3 = st.columns(3)
                            col1.metric("上涨", f"{up_count} 只", f"{up_count/len(valid_changes)*100:.1f}%")
                            col2.metric("下跌", f"{down_count} 只", f"{down_count/len(valid_changes)*100:.1f}%")
                            col3.metric("平盘", f"{flat_count} 只")
                        
                        # 持仓贡献度排行榜
                        st.markdown("#### 🏆 持仓贡献度排行榜")
                        st.caption("贡献度 = 权重% × 涨跌%")
                        
                        # 筛选有涨跌数据的持仓
                        df_contrib = pd.DataFrame([
                            h for h in holdings_data 
                            if h['change_pct'] is not None and h['贡献度'] != 0
                        ])
                        
                        if not df_contrib.empty:
                            # 排序：按贡献度
                            df_contrib = df_contrib.sort_values('贡献度', ascending=False)
                            
                            # 取前10正贡献 + 前5负贡献
                            top_positive = df_contrib[df_contrib['贡献度'] > 0].head(10)
                            top_negative = df_contrib[df_contrib['贡献度'] < 0].tail(5)
                            df_display = pd.concat([top_positive, top_negative])
                            
                            # 柱状图
                            fig = px.bar(
                                df_display,
                                x='name',
                                y='贡献度',
                                color='贡献度',
                                color_continuous_scale=['red', 'yellow', 'green'],
                                color_continuous_midpoint=0,
                                title="",
                                labels={'name': '股票名称', '贡献度': '贡献度(%)'}
                            )
                            fig.update_layout(
                                xaxis_tickangle=-45,
                                height=400,
                                showlegend=False
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("暂无持仓股票数据")
                else:
                    st.info("该产品无持仓数据")
            
            else:
                # ========== 股票详细分析 ==========
                df = get_stock_history(selected, period="6mo")
                if not df.empty:
                    df = add_technical_indicators(df)
                    render_candlestick_chart(df, title=selected)
                else:
                    st.error(f"无法加载 {selected} 的数据")

    # 3. Historical NAV Comparison
    all_funds = [s for s in subs if s.market_type in [MarketType.FUND, MarketType.CN_STOCK] and s.symbol.isdigit()]
    
    if len(all_funds) >= 2:
        st.divider()
        st.subheader("📈 历史净值对比分析")
        
        # 多选框
        selected_funds = st.multiselect(
            "选择基金进行对比（最多4个）",
            [f.symbol for f in all_funds],
            default=[f.symbol for f in all_funds[:2]],
            max_selections=4,
            format_func=lambda x: f"{x} - {next((s.notes or s.symbol for s in all_funds if s.symbol == x), x)}"
        )
        
        if len(selected_funds) >= 2:
            with st.spinner("加载对比数据..."):
                fig = go.Figure()
                stats = []
                
                for symbol in selected_funds:
                    data = get_fund_realtime_data(symbol)
                    history = data.get('history', pd.DataFrame())
                    
                    if not history.empty and len(history) > 0:
                        # 归一化：相对涨跌幅（起点=100）
                        base_nav = history['单位净值'].iloc[0]
                        normalized = (history['单位净值'] / base_nav) * 100
                        
                        fig.add_trace(go.Scatter(
                            x=history.index,
                            y=normalized,
                            name=data.get('name', symbol),
                            mode='lines+markers',
                            line=dict(width=2),
                            marker=dict(size=4)
                        ))
                        
                        # 计算统计数据
                        latest_nav = data.get('latest_nav', 0)
                        period_change = ((latest_nav - base_nav) / base_nav * 100) if base_nav > 0 else 0
                        
                        stats.append({
                            "基金": data.get('name', symbol),
                            "最新净值": f"¥{latest_nav:.4f}",
                            "当日涨跌": f"{data.get('change_pct', 0):+.2f}%",
                            "区间涨跌": f"{period_change:+.2f}%"
                        })
                
                fig.update_layout(
                    title="净值走势对比（起点=100）",
                    yaxis_title="相对净值",
                    xaxis_title="日期",
                    hovermode='x unified',
                    height=500,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 对比统计表格
                if stats:
                    st.markdown("#### 对比统计")
                    st.dataframe(stats, use_container_width=True, hide_index=True)
        else:
            st.info("请至少选择2个基金进行对比")

    db.close()
    
    # Auto-refresh logic (at the end)
    if auto_refresh:
        time.sleep(30)
        st.rerun()


def render_admin():
    st.header("Database Monitor 🛠️")
    
    if st.button("Refresh Database Stats"):
        db = next(get_db())
        from src.database.models import User, Subscription
        
        u_count = db.query(User).count()
        s_count = db.query(Subscription).count()
        
        col1, col2 = st.columns(2)
        col1.metric("Total Users", u_count)
        col2.metric("Total Subscriptions", s_count)
        
        st.subheader("Users")
        users = db.query(User).all()
        st.dataframe([{"ID": u.id, "Username": u.username, "Created": u.created_at} for u in users])
        
        st.subheader("Subscriptions")
        subs = db.query(Subscription).all()
        st.dataframe([{"ID": s.id, "User": s.user.username, "Symbol": s.symbol} for s in subs])
        
        db.close()
