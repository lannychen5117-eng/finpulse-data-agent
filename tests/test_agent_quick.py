#!/usr/bin/env python3
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

print("Testing agent creation...")
try:
    from src.agent.core import create_agent_executor
    agent = create_agent_executor()
    print(f"✅ Agent created successfully: {type(agent)}")
    
    print("\nTesting agent invoke...")
    from langchain_core.messages import HumanMessage
    result = agent.invoke({"messages": [HumanMessage(content="Hello")]})
    print(f"✅ Agent invoked successfully")
    print(f"Response type: {type(result)}")
    print(f"Keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
    if isinstance(result, dict) and "messages" in result:
        print(f"Message count: {len(result['messages'])}")
        print(f"Last message: {result['messages'][-1].content[:100]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
