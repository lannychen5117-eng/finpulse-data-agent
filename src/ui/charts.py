import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st

def render_candlestick_chart(df: pd.DataFrame, title: str = "Stock Price"):
    """
    Renders an interactive candlestick chart with volume and technical indicators.
    """
    if df.empty:
        st.warning(f"No data available for {title}")
        return

    # Create subplots: 1. Main Chart (Price), 2. Volume, 3. RSI, 4. MACD
    fig = make_subplots(
        rows=4, cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f"{title} Price", "Volume", "RSI (14)", "MACD"),
        row_heights=[0.5, 0.1, 0.2, 0.2]
    )

    # 1. Candlestick Chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='OHLC'
    ), row=1, col=1)

    # SMA Overlays
    if 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='orange', width=1), name='SMA 20'), row=1, col=1)
    if 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='blue', width=1), name='SMA 50'), row=1, col=1)
    
    # Bollinger Bands
    if 'BBU_20_2.0' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['BBU_20_2.0'], line=dict(color='gray', width=0), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BBL_20_2.0'], line=dict(color='gray', width=0), fill='tonexty', fillcolor='rgba(128,128,128,0.2)', name='Bollinger Bands'), row=1, col=1)

    # 2. Volume Chart
    colors = ['green' if row['Close'] >= row['Open'] else 'red' for index, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume'), row=2, col=1)

    # 3. RSI Chart
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name='RSI'), row=3, col=1)
        # Add 70/30 lines
        fig.add_shape(type="line", x0=df.index[0], x1=df.index[-1], y0=70, y1=70, line=dict(color="red", width=1, dash="dash"), row=3, col=1)
        fig.add_shape(type="line", x0=df.index[0], x1=df.index[-1], y0=30, y1=30, line=dict(color="green", width=1, dash="dash"), row=3, col=1)

    # 4. MACD Chart
    if 'MACD' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='blue', width=1.5), name='MACD'), row=4, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_signal'], line=dict(color='orange', width=1.5), name='Signal'), row=4, col=1)
        # Histogram
        colors = ['green' if (val >= 0) else 'red' for val in (df['MACD'] - df['MACD_signal'])]
        fig.add_trace(go.Bar(x=df.index, y=(df['MACD'] - df['MACD_signal']), marker_color=colors, name='Histogram'), row=4, col=1)

    # Layout Updates
    fig.update_layout(
        height=800,
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

def render_sparkline(df: pd.DataFrame, title: str, value: str, delta: str):
    """
    Renders a metric card with a sparkline chart.
    """
    if df.empty:
        return

    # Create a small line chart
    fig = px.line(df, x=df.index, y='Close')
    
    # Update layout to be minimal (sparkline style)
    color = "green" if float(delta.strip('%')) >= 0 else "red"
    
    fig.update_traces(line_color=color, line_width=2)
    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=50,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Display using Streamlit metric and chart
    st.markdown(f"""
    <div style="padding: 10px; border-radius: 5px; background-color: #1E1E1E; border: 1px solid #333; margin-bottom: 10px;">
        <h4 style="margin: 0; color: #888; font-size: 14px;">{title}</h4>
        <div style="display: flex; align_items: baseline; justify-content: space-between;">
            <h2 style="margin: 0; font-size: 24px; color: #FFF;">{value}</h2>
            <span style="color: {color}; font-weight: bold;">{delta}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_portfolio_summary(subscriptions: list):
    """
    Renders a summary of the portfolio (if we had position sizes, we'd do a pie chart).
    For now, just a nice table.
    """
    if not subscriptions:
        return

    df = pd.DataFrame(subscriptions)
    if df.empty:
        return

    st.subheader("Portfolio Distribution")
    
    # Since we don't have value, just show count by type
    if 'Type' in df.columns:
        fig = px.pie(df, names='Type', title='Asset Allocation by Type', hole=0.4, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
