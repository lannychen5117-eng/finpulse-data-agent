import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.core import create_agent_executor
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def test_agent():
    print("--- Testing Agent Loop ---")
    try:
        agent_executor = create_agent_executor()
        print("Agent created.")
        
        query = "What is the price of AAPL?"
        print(f"Invoking agent with: {query}")
        
        # We use invoke
        result = agent_executor.invoke({"input": query, "chat_history": []})
        print(f"Result: {result['output']}")
        
        if "No data" in result['output'] or "Error" in result['output']:
             print("Agent might have failed to use tool.")
        else:
             print("Agent seems to have worked.")
             
    except Exception as e:
        print(f"Agent Loop Error: {e}")

if __name__ == "__main__":
    test_agent()
