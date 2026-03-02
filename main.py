import re
import time
import random
import getpass
import threading
import rich.prompt
from datetime import datetime
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich.markdown import Markdown
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
    gemini_api_key = rich.prompt.Prompt.ask("Enter Gemini API key (or press Enter to skip)").strip()
    if gemini_api_key:
        config.gemini_api_key = gemini_api_key
        set_setting('GEMINI_API_KEY', gemini_api_key)

if not config.groq_api_key:
    groq_api_key = rich.prompt.Prompt.ask("Enter Groq API key (or press Enter to skip)").strip()
    if groq_api_key:
        config.groq_api_key = groq_api_key
        set_setting('GROQ_API_KEY', groq_api_key)

if not config.provider:
    available_providers = []
    if config.gemini_api_key:
        available_providers.append('gemini')
    if config.groq_api_key:
        available_providers.append('groq')
    
    if not available_providers:
        console.print("[red bold]No API keys provided. Please restart and enter at least one API key.[/red bold]")
        exit(1)
    
    if len(available_providers) == 1:
        config.provider = available_providers[0]
        set_setting('PROVIDER', config.provider)
    else:
        provider = rich.prompt.Prompt.ask(f"Select preferred provider [{'/'.join(available_providers)}]", choices=available_providers).strip()
        config.provider = provider
        set_setting('PROVIDER', provider)

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
    sleep_time = 0.03
    for i in range(len(greeting) + 1):
        cursor = "_" if i < len(greeting) else ""
        print(f"\r {greeting[:i]}{cursor}", end="", flush=True)
        if i < len(greeting) and greeting[i] in " ":
            time.sleep(random.uniform(sleep_time, sleep_time*3))
        time.sleep(sleep_time)
    
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
    
    from agent.agent import chat, agent_monitoring
    import database
    
    stop_animation = True
    
    for i in range(len(greeting), -1, -1):
        print(f"\r {greeting[:i]}_ ", end="", flush=True)
        time.sleep(0.015)
    
    print("\033[0m", end="")
    print("\r" + " " * (len(greeting) + 4), end="\r")
    console.clear()
    
    return chat, agent_monitoring, database



def show_logo():
    width = console.width
    inscriptions = locales.focus_agent_inscription
    
    if width >= inscriptions['ansi_shadow']['length']:
        logo = inscriptions['ansi_shadow']['text']
    elif width >= inscriptions['ansi_compact']['length']:
        logo = inscriptions['ansi_compact']['text']
    else:
        logo = inscriptions['normal']['text']
    
    lines = logo.split('\n')
    max_line_length = max(len(line) for line in lines)
    
    for line in lines:
        padding = (width - max_line_length) // 2
        console.print(' ' * padding + line)


chat, agent_monitoring, database = show_greeting_with_loading(config.username)  # Very messy code, but a beautiful result, so who cares?
show_logo()

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
            console.print("\n\n[cyan bold]Goodbye[/cyan bold]")
            break
        
        database.save_message('user', user_input)
        
        recent_messages = database.get_messages(limit=10)
        messages = [{'role': msg['role'], 'content': msg['content']} for msg in reversed(recent_messages)]
        
        with console.status("[cyan bold]Generating...[/cyan bold]", spinner="dots", spinner_style="cyan"):
            response, used_functions = chat(user_input, messages=messages)
        
        database.save_message('model', response)
        
        if used_functions:
            print("\n\033[90mUsed functions:\033[0m")
            for func in used_functions:
                args_str = ", ".join(f"{k}={v}" for k, v in func['args'].items())
                print(f"  \033[32m✓\033[0m {func['name']}({args_str})")
        
        parts = re.split(r'(\n)', response)
        current_text = ""
        
        with Live(console=console, refresh_per_second=20) as live:
            for part in parts:
                if part == '\n':
                    current_text += part
                else:
                    words = part.split(' ')
                    for word in words:
                        current_text += word + " "
                        markdown_response = Markdown(current_text)
                        panel = Panel(
                            markdown_response,
                            title="[cyan bold]FocusAgent[/cyan bold]",
                            border_style="cyan",
                            padding=(1, 2)
                        )
                        live.update(panel)
                        time.sleep(0.005)
        
    except KeyboardInterrupt:
        console.print("\n\n[cyan bold]Goodbye[/cyan bold]")
        break
    except Exception as e:
        console.print(f"\n[red bold]Error: {e}[/red bold]")

