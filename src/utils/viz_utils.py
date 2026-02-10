
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import os
import uuid
from typing import Optional, List, Dict, Any

class VizUtils:
    """
    Utility class for generating financial charts and visualizations.
    """
    
    def __init__(self, output_dir: str = "public/charts"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def _save_chart(self, fig: go.Figure, title: str) -> str:
        """
        Saves the chart to an HTML file and returns the relative path.
        """
        filename = f"{title.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)
        return filepath

    def create_candlestick_chart(self, df: pd.DataFrame, title: str = "Stock Price History") -> str:
        """
        Creates a candlestick chart from a DataFrame.
        Expects columns: 'Open', 'High', 'Low', 'Close' (and 'Date' index or column).
        """
        if 'Date' not in df.columns and not isinstance(df.index, pd.DatetimeIndex):
             # Try to reset index if Date is index
             df = df.reset_index()
             
        date_col = 'Date' if 'Date' in df.columns else df.columns[0]
        
        fig = go.Figure(data=[go.Candlestick(x=df[date_col],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])

        fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Price")
        return self._save_chart(fig, title)

    def create_line_chart(self, df: pd.DataFrame, x_col: str, y_cols: List[str], title: str = "Line Chart") -> str:
        """
        Creates a multi-line chart.
        """
        fig = go.Figure()
        for col in y_cols:
            fig.add_trace(go.Scatter(x=df[x_col], y=df[col], mode='lines', name=col))
            
        fig.update_layout(title=title, xaxis_title=x_col, yaxis_title="Value")
        return self._save_chart(fig, title)
    
    def create_bar_chart(self, x_data: List[Any], y_data: List[Any], x_label: str, y_label: str, title: str = "Bar Chart") -> str:
        """
        Creates a simple bar chart.
        """
        fig = go.Figure(data=[go.Bar(x=x_data, y=y_data)])
        fig.update_layout(title=title, xaxis_title=x_label, yaxis_title=y_label)
        return self._save_chart(fig, title)
