"""
Agent Core Module
Creates the FinPulse agent executor using LangGraph.
"""
import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langgraph.prebuilt import create_react_agent

# Load environment variables from .env file
load_dotenv()

from src.agent.prompts import SYSTEM_PROMPT
from src.agent.skill_manager import SkillManager

def create_agent_executor():
    """
    Creates and returns the FinPulse agent executor using Nvidia LLM.
    Uses LangGraph's create_react_agent.
    """
    model_name = os.getenv("NVIDIA_MODEL_NAME", "meta/llama3-70b-instruct")
    base_url = os.getenv("NVIDIA_BASE_URL")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    
    # Initialize Nvidia Chat Model
    llm = ChatNVIDIA(
        model=model_name,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # Load dynamic skills
    skill_manager = SkillManager()
    all_tools = skill_manager.load_skills()
    
    # LangGraph's create_react_agent accepts 'prompt' parameter (system message)
    agent = create_react_agent(
        llm, 
        all_tools,
        prompt=SYSTEM_PROMPT
    )
    
    return agent
