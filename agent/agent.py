from agent.gemini import gemini
from agent.groq import groq
from config import config
    

def chat(user_message, tools_list=None, messages=None, max_iterations=10):
    """Send a message to the agent and handle function calling loop
    
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
    
    providers = [
        (config.provider, gemini if config.provider == 'gemini' else groq),
        ('gemini' if config.provider != 'gemini' else 'groq', groq if config.provider == 'gemini' else gemini)
    ]
    
    for provider_name, provider_func in providers:
        try:
            return provider_func(user_message, tools_list, messages, max_iterations)
        except Exception as e:
            print(f"\033[1;31m{provider_name} failed: {e}\033[0m")
            continue
    
    return "All providers failed. Please try again.", []


def agent_monitoring():
    """Monitoring mode: check windows and decide if action needed
    
    Returns:
        tuple: (response_text, list of used functions with args)
    """
    import system_api
    import database
    from datetime import datetime
    
    windows = system_api.get_windows()
    database.log_monitoring(windows)
    logs = database.get_monitoring_logs(hours_back=1)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    recent_messages = database.get_messages(limit=10)
    messages = [{'role': msg['role'], 'content': msg['content']} for msg in reversed(recent_messages)]
    
    prompt = config.monitoring_prompt.format(
        current_time=current_time,
        windows=windows,
        logs=logs
    )
    
    return chat(prompt, tools_list=config.monitoring_tools, messages=messages)


# TODO: необходимо записывать если агент решает закрыть приложение. Записывать нужно со временем, но тогда и нужно время сообщений и добавить новую таблицу agent_actions