import time
import random
from datetime import datetime
from rich.console import Console
from config import config, locales

console = Console()


def get_greeting(username):
    hour = datetime.now().hour
    lang = config.language
    
    if 5 <= hour < 12:
        return locales.morning_greeting[lang].format(username=username)
    elif 12 <= hour < 18:
        return locales.afternoon_greeting[lang].format(username=username)
    elif 18 <= hour < 22:
        return locales.evening_greeting[lang].format(username=username)
    else:
        return locales.night_greeting[lang].format(username=username)

def animate_greeting(username="User"):
    greeting = get_greeting(username)
    console.clear()
    print("\033[1;36m")  # cyan bold
    print()
    for i in range(len(greeting) + 1):
        cursor = "_" if i < len(greeting) else ""
        print(f"\r  {greeting[:i]}{cursor}", end="", flush=True)
        if i < len(greeting) and greeting[i] in " ":
            time.sleep(random.uniform(0.04, 0.12))
        time.sleep(0.04)
    
    for _ in range(6):
        print(f"\r  {greeting}_", end="", flush=True)
        time.sleep(0.15)
        print(f"\r  {greeting} ", end="", flush=True)
        time.sleep(0.15)
    
    for i in range(len(greeting), -1, -1):
        print(f"\r  {greeting[:i]}_ ", end="", flush=True)
        time.sleep(0.02)
    
    print("\033[0m", end="")  # reset
    print("\r" + " " * (len(greeting) + 4), end="\r")
    console.clear()

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


if __name__ == "__main__":
    animate_greeting("Test User")
    show_logo()