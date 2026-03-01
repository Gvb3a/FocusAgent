import json
import database
import system_api
import rich.prompt
from pathlib import Path
from dataclasses import dataclass


base_dir = Path(__file__).parent
env_settings = database.get_env_settings()

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)



FUNCTION_MAP = {
    # Activities
    "create_activity": database.create_activity,
    "get_activities": database.get_activities,
    "update_activity": database.update_activity,
    "delete_activity": database.delete_activity,
    
    # Exercises
    "get_all_exercises": database.get_all_exercises,
    "find_exercise": database.find_exercise,
    "create_exercise": database.create_exercise,
    "update_exercise": database.update_exercise,
    "delete_exercise": database.delete_exercise,
    
    # Workouts
    "create_workout": database.create_workout,
    "get_workouts": database.get_workouts,
    "update_workout": database.update_workout,
    "delete_workout": database.delete_workout,
    
    # System
    "get_time": system_api.get_time_str,
    "get_all_windows": system_api.get_all_windows,
    "close_browser": system_api.close_browser,
    "close_app": system_api.close_app,
    
    # Monitoring
    "log_monitoring": database.log_monitoring,
    "get_monitoring_logs": database.get_monitoring_logs,
    
    # Memory
    "get_memory": database.get_memory,
    "update_memory": database.update_memory,
    "add_to_memory": database.add_to_memory,
}

@dataclass
class Config:
    database_path: str = str(base_dir / "activities.db")
    function_declarations_path: str = str(base_dir / "function_declarations.json")
    prompts_path: str = str(base_dir / "prompts.json")
    locales_path: str = str(base_dir / "locales.json")
    log_path: str = str(base_dir / "agent.log")

    language: str = env_settings['LANGUAGE']
    gemini_api_key: str = env_settings['GEMINI_API_KEY']
    gemini_model: str = env_settings['GEMINI_MODEL']

    monitoring_interval: int = 600

    conversation_tools: list = None
    monitoring_tools: list = None
    api_key_warning: str = ""
    
    system_prompt: str = ""
    monitoring_prompt: str = ""

    def __post_init__(self):
        # Load prompts
        prompts = load_json('prompts.json')
        self.system_prompt = prompts['system_prompt']
        self.monitoring_prompt = prompts['monitoring_prompt']
        
        if self.conversation_tools is None:
            self.conversation_tools = [
                "get_activities",
                "create_activity",
                "update_activity",
                "delete_activity",
                
                "get_all_exercises",
                "find_exercise",
                "create_exercise",
                "update_exercise",
                "delete_exercise",

                "create_workout",
                "get_workouts",
                "update_workout",
                "delete_workout",

                "get_monitoring_logs",

                "get_memory",
                "update_memory",
                "add_to_memory",
            ]
        
        if self.monitoring_tools is None:
            self.monitoring_tools = [
                "close_browser",
                "close_app",
                "get_activities",
                "create_activity",
                "update_activity",
                "delete_activity",
            ]


config = Config()


@dataclass
class Locales:
    gemini_api_warning: dict = None

    def __post_init__(self):
        with open(base_dir / "locales.json", "r") as f:
            data = json.load(f)
            self.gemini_api_warning = data["gemini_api_warning"]


locales = Locales()


if not config.gemini_api_key:
    gemini_api_key = rich.prompt.Prompt.ask(locales.gemini_api_warning[config.language]).strip()
    config.gemini_api_key = gemini_api_key
    database.set_setting('GEMINI_API_KEY', gemini_api_key)

