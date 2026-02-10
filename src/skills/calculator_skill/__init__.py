from langchain.tools import tool

@tool
def calculator_tool(expression: str) -> str:
    """
    Calculates the result of a mathematical expression.
    Useful for performing simple calculations.
    """
    try:
        # Evaluate the expression safely
        allowed_names = {"abs": abs, "round": round}
        code = compile(expression, "<string>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                raise NameError(f"Use of {name} is not allowed")
        
        result = eval(code, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

# Export the tools provided by this skill
TOOLS = [calculator_tool]
