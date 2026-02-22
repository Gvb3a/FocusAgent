import os
import json
import rich
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass


load_dotenv()
base_dir = Path(__file__).parent


@dataclass
class Config:
    database_path: str = str(base_dir / "activities.db")
    function_declarations_path: str = str(base_dir / "function_declarations.json")
    locales_path: str = str(base_dir / "locales.json")
    log_path: str = str(base_dir / "agent.log")

    language: str = os.getenv("LANGUAGE", "en")
    gemini_api_key: str = os.getenv("GEMINI_API_KE", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    monitoring_interval: int = 600

    conversation_tools: list = None
    monitoring_tools: list = None
    api_key_warning: str = ""

    def __post_init__(self):
        if self.conversation_tools is None:
            self.conversation_tools = [
                "get_activities",
                "create_activity",
                "update_activity",
                "delete_activity",

                "get_monitoring_logs",

                "create_workout",
                "get_workouts",
                "get_all_exercises",
                "find_exercise",
                "create_exercise",

                "get_memory",
                "update_memory",
                "add_to_memory"
            ]
        
        if self.monitoring_tools is None:
            self.monitoring_tools = [
                "close_browser",
                "close_app",

                "get_activities",
                "create_activity",
                "update_activity"
                "delete_activity",
            ]


config = Config()


@dataclass
class Locales:
    gemini_api_warning: dict = None

    def __post_init__(self):
        with open(base_dir / "locales.json", "r") as f:
            data = json.load(f)
            self.gemini_api_warning = data.get("gemini_api_warning", {})


locales = Locales()


if not config.gemini_api_key:
    rich.print(locales.gemini_api_warning[config.language])
