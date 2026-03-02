import os
import json
import database
from datetime import datetime
from google import genai
from google.genai import types
from config import config, FUNCTION_MAP


client = genai.Client(api_key=config.gemini_api_key)
os.environ['GRPC_DNS_RESOLVER'] = 'native'


def load_function_declarations():
    """Load function declarations from JSON file"""
    with open(config.function_declarations_path, 'r') as f:
        return json.load(f)


def _convert_messages(messages):
    """Convert simple message format to Gemini Content format
    
    Args:
        messages: List of dicts with 'role' and 'content' keys
                  [{'role': 'user', 'content': 'Hello'}, {'role': 'model', 'content': 'Hi'}]
    
    Returns:
        List of types.Content objects
    """
    if not messages:
        return []
    
    contents = []
    for msg in messages:
        contents.append(types.Content(
            role=msg['role'],
            parts=[types.Part(text=msg['content'])]
        ))
    return contents


def execute_function(function_call):
    """Execute a function call and return the result and call info"""
    function_name = function_call.name
    function_args = dict(function_call.args)
    
    if function_name not in FUNCTION_MAP:
        print(f"\033[1;31m◉ Failed: Function {function_name} not found\033[0m")
        return {"error": f"Function {function_name} not found"}, {"name": function_name, "args": function_args}
    
    try:
        result = FUNCTION_MAP[function_name](**function_args)
        return {"result": result}, {"name": function_name, "args": function_args}
    except Exception as e:
        print(f"\033[1;31m◉ Error executing {function_name}: {e}\033[0m")
        return {"error": str(e)}, {"name": function_name, "args": function_args}
    

def gemini(user_message, tools_list=None, messages=None, max_iterations=10):
    """
    Send a message to the agent and handle function calling loop
    
    Args:
        user_message: User's message
        tools_list: List of tool names to use (defaults to conversation_tools)
        messages: Previous conversation messages in format [{'role': 'user', 'content': '...'}, ...]
        max_iterations: Maximum number of function calling iterations
    
    Returns:
        Final text response from the model
    """
    if tools_list is None:
        tools_list = config.conversation_tools
    
    all_declarations = load_function_declarations()
    declarations = [d for d in all_declarations if d['name'] in tools_list]
    tools = types.Tool(function_declarations=declarations)
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_memory = database.get_memory() or "No memory stored yet."
    system_prompt = config.system_prompt.format(
        current_time=current_time,
        user_memory=user_memory
    )
    
    gen_config = types.GenerateContentConfig(
        tools=[tools],
        system_instruction=system_prompt
    )
    
    # Convert messages to Gemini format and add new user message
    if messages:
        contents = _convert_messages(messages)
        contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))
    else:
        contents = [types.Content(role="user", parts=[types.Part(text=user_message)])]
    
    used_functions = []
    iteration = 0
    while iteration < max_iterations:
        iteration += 1
        
        response = client.models.generate_content(
            model=config.gemini_model,
            contents=contents,
            config=gen_config,
        )
        
        parts = response.candidates[0].content.parts
        function_calls = [p.function_call for p in parts if p.function_call]
        
        if not function_calls:
            return response.text, used_functions

        contents.append(response.candidates[0].content)
        
        for function_call in function_calls:
            result, func_info = execute_function(function_call)
            used_functions.append(func_info)
            function_response = types.Part.from_function_response(
                name=function_call.name,
                response=result
            )
            contents.append(types.Content(role="user", parts=[function_response]))
    
    print("\033[1;31mERROR: Max iterations reached\033[0m")
    return "Max iterations reached. Please try again.", used_functions

