import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langgraph.prebuilt import create_react_agent

# Load environment variables from .env file
load_dotenv()

from src.agent.tools import TOOLS
from src.agent.prompts import SYSTEM_PROMPT

def create_agent_executor():
    """
    Creates and returns the FinPulse agent executor using Nvidia LLM.
    Note: Using LangGraph's create_react_agent which returns a compiled graph.
    """
    model_name = os.getenv("NVIDIA_MODEL_NAME", "meta/llama3-70b-instruct")
    base_url = os.getenv("NVIDIA_BASE_URL")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1024"))
    
    # Initialize Nvidia Chat Model
    llm = ChatNVIDIA(
        model=model_name,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # LangGraph's create_react_agent accepts 'prompt' parameter
    # Can be a string, SystemMessage, or callable
    # We'll pass SYSTEM_PROMPT as a string directly
    agent = create_react_agent(
        llm, 
        TOOLS,
        prompt=SYSTEM_PROMPT
    )
    
    return agent
