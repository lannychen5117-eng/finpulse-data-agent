import streamlit as st
import os
import sys
import re
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import our agent creator
from src.agent.core import create_agent_executor

# Load environment variables
load_dotenv()

from src.auth.auth import login_user, register_user
from src.ui.dashboard import render_dashboard, render_admin
from src.ui.charts import render_candlestick_chart
from src.data.stock import get_stock_history
from src.analysis.technical import add_technical_indicators

def extract_ticker(text: str):
    """
    Extracts a likely stock ticker or fund code from text.
    Prioritizes uppercase 2-5 letter codes or 6 digit codes.
    """
    # Common ignore words (expanded)
    ignore = {
        "AND", "FOR", "THE", "HAS", "WAS", "NOT", "YES", "BUY", "SELL", "HOLD", "NOW", 
        "ARE", "WHO", "WHAT", "WHY", "HOW", "TELL", "ME", "ABOUT", "THIS", "THAT", 
        "WITH", "FROM", "INTO", "OVER", "UNDER", "CAN", "YOU", "PLEASE", "SHOW", "CHECK",
        "ANALYSIS", "ANALYZE", "TREND", "STOCK", "FUND", "MARKET", "PRICE", "UPDATE"
    }
    
    # Regex for potential tickers:
    # 1. Futures: GC=F, RB0, etc.
    futures_math = re.search(r'\b([A-Z]{2}=F|[A-Z]{2,3}[0-9]+)\b', text)
    if futures_math:
        return futures_math.group(1)
        
    # 2. Codes: 
    # - 6 digits (CN funds/stocks): 000001
    # - 4 digits + .HK: 2800.HK
    # - 6 digits + .SS/SZ: 000001.SS
    code_match = re.search(r'\b([0-9]{6}(\.[A-Z]{2})?|[0-9]{4}\.HK)\b', text)
    if code_match:
        return code_match.group(1)
        
    # 3. US tickers (All caps, 2-5 letters)
    # We filter out common words
    matches = re.findall(r'\b[A-Z]{2,5}\b', text)
    for m in matches:
        if m not in ignore:
            return m
            
    return None

def render_chart_if_needed(prompt: str):
    """
    Checks if the user asked for analysis and renders a chart if a ticker is found.
    """
    trigger_words = {"analyze", "chart", "price", "technical", "trend", "show", "check"}
    if any(w in prompt.lower() for w in trigger_words):
        ticker = extract_ticker(prompt)
        if ticker:
            with st.expander(f"📊 Market Chart: {ticker}", expanded=True):
                with st.spinner(f"Generating chart for {ticker}..."):
                    try:
                        # Try to get data
                        df = get_stock_history(ticker, period="6mo")
                        if not df.empty:
                            df = add_technical_indicators(df)
                            render_candlestick_chart(df, title=ticker)
                        else:
                            st.info(f"No chart data available for {ticker}")
                    except Exception as e:
                        st.error(f"Could not load chart: {e}")

def init_page():
    st.title("FinPulse Data Agent 📈")
    if "user" in st.session_state:
        st.caption(f"Logged in as: {st.session_state['user']['username']}")

def login_page():
    st.title("FinPulse Data Agent 🔐")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                result = login_user(username, password)
                if result["success"]:
                    st.session_state["user"] = result["user"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(result["message"])

    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password")
            new_email = st.text_input("Email (Required)")
            reg_submitted = st.form_submit_button("Register")
            
            if reg_submitted:
                if not new_user or not new_pass or not new_email:
                    st.error("Username, Password, and Email are required.")
                else:
                    result = register_user(new_user, new_pass, new_email)
                    if result["success"]:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(result["message"])

def sidebar():
    with st.sidebar:
        st.header("Configuration")
        
        # Check for API Key
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            api_key = st.text_input("Enter Nvidia API Key", type="password")
            if api_key:
                os.environ["NVIDIA_API_KEY"] = api_key
        
        st.divider()
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
            
        st.markdown("### Suggested Queries")
        suggestions = [
            "Analyze AAPL stock",
            "What is the latest news on Tesla?",
            "Compare Google and Microsoft fundamentals",
            "Show me the price of Gold and Oil",
            "Is NVIDIA overbought according to RSI?",
            "Analyze my funds",
            "Analyze futures RB0"
        ]
        for s in suggestions:
            if st.button(s):
                st.session_state.prompt_input = s

def main():
    st.set_page_config(page_title="FinPulse Data Agent", layout="wide", page_icon="📈")
    
    if "user" not in st.session_state:
        login_page()
        return

    # Sidebar Navigation
    with st.sidebar:
        st.title("FinPulse")
        st.caption(f"Logged in as: {st.session_state['user']['username']}")
        
        page = st.radio("Navigation", ["Chat", "Dashboard", "Admin Monitor"])
        
        if st.button("Logout"):
            del st.session_state["user"]
            st.rerun()
        st.divider()
        
    if page == "Chat":
        init_page()
        sidebar() # Chat specific sidebar items
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Initialize Agent (cached resource)
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            st.warning("⚠️ **Missing Configuration**: `NVIDIA_API_KEY` is not set.")
            st.info("Please set `NVIDIA_API_KEY` in your `.env` file or enter it in the sidebar.")
        elif "agent" not in st.session_state:
            try:
                st.session_state.agent = create_agent_executor()
            except Exception as e:
                st.error(f"Failed to initialize agent: {e}")
                return

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                # Check for chart markers or context (could be stored in message metadata in future)

        # Chat Input
        if "prompt_input" in st.session_state:
            prompt = st.session_state.prompt_input
            del st.session_state.prompt_input
        else:
            prompt = st.chat_input("输入问题（如：分析苹果股票、订阅茅台）...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                if "agent" not in st.session_state:
                     st.error("Agent 未初始化，请检查配置。")
                else: 
                    with st.spinner("正在分析数据..."):
                        try:
                            from langchain_core.messages import HumanMessage as HMsg
                            from src.agent.user_context import UserContext, set_user_context
                            
                            # Set user context before invoking agent
                            user_ctx = UserContext.from_session()
                            set_user_context(user_ctx)
                            print(f"[DEBUG app.py] User context set: user_id={user_ctx.user_id if user_ctx else None}")
                            
                            # Use LangGraph message-based API
                            result = st.session_state.agent.invoke(
                                {"messages": [HMsg(content=prompt)]}
                            )

                            output = result["messages"][-1].content
                            
                            # Display text response
                            st.markdown(output)
                            st.session_state.messages.append({"role": "assistant", "content": output})
                            
                            # Enhanced chart rendering - detect if analysis was performed
                            analysis_keywords = ["分析", "analyze", "技术", "technical", "报告", "chart", "图表"]
                            if any(kw in prompt.lower() or kw in output.lower() for kw in analysis_keywords):
                                ticker = extract_ticker(prompt) or extract_ticker(output)
                                if ticker:
                                    with st.expander(f"📊 {ticker} 详细图表", expanded=True):
                                        try:
                                            df = get_stock_history(ticker, period="6mo")
                                            if not df.empty:
                                                df = add_technical_indicators(df)
                                                render_candlestick_chart(df, title=ticker)
                                            else:
                                                st.info(f"暂无 {ticker} 的图表数据")
                                        except Exception as chart_e:
                                            st.error(f"图表加载失败: {chart_e}")
                            
                        except Exception as e:
                            st.error(f"发生错误: {e}")
                            import traceback
                            st.code(traceback.format_exc())
                        
    elif page == "Dashboard":
        render_dashboard()
        
    elif page == "Admin Monitor":
        render_admin()

if __name__ == "__main__":
    main()

