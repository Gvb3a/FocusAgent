import getpass
import rich.prompt
import threading
import time
import random
from datetime import datetime
from rich.console import Console
from config import config, locales
from database import set_setting


console = Console()


if not config.language:
    language = rich.prompt.Prompt.ask('Language not specified. Type “en” or Enter to select English, “ru” for Russian').strip()
    if not language:
        language = 'en'
    elif language not in ['en', 'ru']:
        console.print(f"[red bold]Invalid language. Defaulting to English.[/red bold]")
        language = 'en'
    config.language = language
    set_setting('LANGUAGE', language)


if not config.gemini_api_key:
    gemini_api_key = rich.prompt.Prompt.ask(locales.gemini_api_warning[config.language]).strip()
    config.gemini_api_key = gemini_api_key
    set_setting('GEMINI_API_KEY', gemini_api_key)

if not config.username:
    username = rich.prompt.Prompt.ask(locales.username_warning[config.language].format(username=getpass.getuser())).strip()
    if not username:
        username = getpass.getuser()
    config.username = username
    set_setting('USERNAME', username)


def show_greeting_with_loading(username):
    hour = datetime.now().hour
    lang = config.language
    
    if 5 <= hour < 12:
        greeting = locales.morning_greeting[lang].format(username=username)
    elif 12 <= hour < 18:
        greeting = locales.afternoon_greeting[lang].format(username=username)
    elif 18 <= hour < 22:
        greeting = locales.evening_greeting[lang].format(username=username)
    else:
        greeting = locales.night_greeting[lang].format(username=username)
    
    console.clear()
    print("\033[1;36m")
    
    for i in range(len(greeting) + 1):
        cursor = "_" if i < len(greeting) else ""
        print(f"\r {greeting[:i]}{cursor}", end="", flush=True)
        if i < len(greeting) and greeting[i] in " ":
            time.sleep(random.uniform(0.04, 0.12))
        time.sleep(0.04)
    
    stop_animation = False
    def animate_dots():
        dots = ["", ".", "..", "..."]
        idx = 0
        while not stop_animation:
            print(f"\r {greeting}{dots[idx % len(dots)]}  ", end="", flush=True)
            idx += 1
            time.sleep(0.3)
    
    dot_thread = threading.Thread(target=animate_dots, daemon=True)
    dot_thread.start()
    
    from agent import chat, agent_monitoring
    import database
    
    stop_animation = True
    time.sleep(0.1)
    
    for i in range(len(greeting), -1, -1):
        print(f"\r {greeting[:i]}_ ", end="", flush=True)
        time.sleep(0.015)
    
    print("\033[0m", end="")
    print("\r" + " " * (len(greeting) + 4), end="\r")
    console.clear()
    
    return chat, agent_monitoring, database

chat, agent_monitoring, database = show_greeting_with_loading(config.username)  # Very messy code, but a beautiful result, so who cares?


def monitoring_loop():
    while True:
        time.sleep(config.monitoring_interval)
        try:
            agent_monitoring()
        except Exception as e:
            console.print(f"[red]Monitoring error: {e}[/red]")

monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
monitoring_thread.start()

while True:
    try:
        user_input = rich.prompt.Prompt.ask("\n[green]You[/green]").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['exit', 'quit', 'выход']:
            break
        
        database.save_message('user', user_input)
        
        recent_messages = database.get_messages(limit=10)
        messages = [{'role': msg['role'], 'content': msg['content']} for msg in reversed(recent_messages)]
        
        with console.status("[cyan]...[/cyan]", spinner="dots", spinner_style="cyan"):
            response = chat(user_input, messages=messages)
        
        database.save_message('model', response)
        
        console.print(f"\n🤖 [cyan bold]FocusAgent:[/cyan bold] {response}")
        
    except KeyboardInterrupt:
        console.print("\n\n[cyan bold]Goodbye[/cyan bold]")
        break
    except Exception as e:
        console.print(f"\n[red bold]Error: {e}[/red bold]")


# todo: animation output, 