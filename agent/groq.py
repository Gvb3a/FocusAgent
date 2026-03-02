import json
import database
from datetime import datetime
from groq import Groq
from config import config, FUNCTION_MAP


client = Groq(api_key=config.groq_api_key)


def load_function_declarations():
    """Load and convert function declarations to Groq format"""
    with open(config.function_declarations_path, 'r') as f:
        declarations = json.load(f)
    
    # Convert to Groq format: wrap each in {"type": "function", "function": {...}}
    return [{"type": "function", "function": decl} for decl in declarations]


def execute_function(tool_call):
    """Execute a function call and return the result and call info"""
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    
    if function_name not in FUNCTION_MAP:
        print(f"\033[1;31m◉ Failed: Function {function_name} not found\033[0m")
        return {"error": f"Function {function_name} not found"}, {"name": function_name, "args": function_args}
    
    try:
        result = FUNCTION_MAP[function_name](**function_args)
        return {"result": result}, {"name": function_name, "args": function_args}
    except Exception as e:
        print(f"\033[1;31m◉ Error executing {function_name}: {e}\033[0m")
        return {"error": str(e)}, {"name": function_name, "args": function_args}


def groq(user_message, tools_list=None, messages=None, max_iterations=10):
    """Send a message to Groq and handle function calling loop
    
    Args:
        user_message: User's message
        tools_list: List of tool names to use (defaults to conversation_tools)
        messages: Previous conversation messages
        max_iterations: Maximum number of function calling iterations
    
    Returns:
        tuple: (response_text, list of used functions with args)
    """
    if tools_list is None:
        tools_list = config.conversation_tools
    
    all_declarations = load_function_declarations()
    tools = [t for t in all_declarations if t['function']['name'] in tools_list]
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_memory = database.get_memory() or "No memory stored yet."
    system_prompt = config.system_prompt.format(
        current_time=current_time,
        user_memory=user_memory
    )
    
    # Build messages array
    groq_messages = [{"role": "system", "content": system_prompt}]
    if messages:
        # Convert Gemini format to Groq format (model -> assistant)
        for msg in messages:
            role = "assistant" if msg['role'] == 'model' else msg['role']
            groq_messages.append({"role": role, "content": msg['content']})
    groq_messages.append({"role": "user", "content": user_message})
    
    used_functions = []
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        if not tool_calls:
            return response_message.content, used_functions
        
        # Convert response_message to dict for Groq
        groq_messages.append({
            "role": "assistant",
            "content": response_message.content or "",
            "tool_calls": [{
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            } for tc in tool_calls]
        })
        
        for tool_call in tool_calls:
            result, func_info = execute_function(tool_call)
            used_functions.append(func_info)
            
            groq_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": json.dumps(result)
            })
    
    print("\033[1;31mERROR: Max iterations reached\033[0m")
    return "Max iterations reached. Please try again.", used_functions
