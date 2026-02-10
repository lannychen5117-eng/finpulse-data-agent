from langchain.tools import tool
from src.data.macro import get_macro_summary

@tool
def macro_data_tool() -> str:
    """
    Get a summary of current macroeconomic indicators (Indices, Gold, Oil).
    """
    try:
        df = get_macro_summary()
        return df.to_string(index=False)
    except Exception as e:
        return f"Error fetching macro data: {e}"

TOOLS = [macro_data_tool]
