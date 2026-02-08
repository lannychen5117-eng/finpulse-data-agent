import streamlit as st
import os
import sys
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import our agent creator
from src.agent.core import create_agent_executor

# Load environment variables
load_dotenv()

st.set_page_config(page_title="FinPulse Data Agent", layout="wide", page_icon="📈")

def init_page():
    st.title("FinPulse Data Agent 📈")
    st.markdown("""
    I am an intelligent agent capable of:
    - 📊 **Real-time Data**: Stock prices, news, and macro indicators.
    - 🧠 **Smart Analysis**: Technical estimates (RSI, Trends) and Fundamental insights.
    - 💬 **Natural Query**: Just ask "How is Apple doing?" or "Analyze TSLA".
    """)

def sidebar():
    with st.sidebar:
        st.header("Configuration")
        
        # Check for API Key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            api_key = st.text_input("Enter OpenAI API Key", type="password")
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
        
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
            "Is NVIDIA overbought according to RSI?"
        ]
        for s in suggestions:
            if st.button(s):
                st.session_state.prompt_input = s

def main():
    init_page()
    sidebar()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize Agent (cached resource)
    if "agent" not in st.session_state:
        try:
            st.session_state.agent = create_agent_executor()
        except Exception as e:
            st.error(f"Failed to initialize agent: {e}")
            return

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    # Check if a suggestion was clicked
    if "prompt_input" in st.session_state:
        prompt = st.session_state.prompt_input
        del st.session_state.prompt_input
    else:
        prompt = st.chat_input("Ask about stocks, markets, or economics...")

    if prompt:
        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing market data..."):
                try:
                    # LangGraph agent uses a different API
                    # Input format: {"messages": [HumanMessage(...)]}
                    # It returns: {"messages": [...all messages including response]}
                    from langchain_core.messages import HumanMessage as HMsg
                    
                    result = st.session_state.agent.invoke(
                        {"messages": [HMsg(content=prompt)]}
                    )
                    
                    # Extract the last AI message
                    output = result["messages"][-1].content
                    st.markdown(output)
                    st.session_state.messages.append({"role": "assistant", "content": output})
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    import traceback
                    st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
