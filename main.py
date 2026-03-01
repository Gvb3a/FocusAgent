import getpass
import rich.prompt
from rich.console import Console
from config import config, locales
from database import set_setting
from animation import animate_greeting, show_logo

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


with console.status(locales.launch_message[config.language], spinner="dots", spinner_style="cyan"):
    from agent import chat, agent_monitoring

#animate_greeting(config.username)
show_logo()