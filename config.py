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
    username: str = env_settings['USERNAME']
    gemini_api_key: str = env_settings['GEMINI_API_KEY']
    gemini_model: str = env_settings['GEMINI_MODEL']

    monitoring_interval: int = 600

    conversation_tools: list = None
    monitoring_tools: list = None
    api_key_warning: str = ""  # ?
    
    system_prompt: str = ""
    monitoring_prompt: str = ""

    def __post_init__(self):
        # Load prompts
        prompts = load_json(base_dir / 'prompts.json')
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
    gemini_api_warning: dict[str] = None
    launch_message: dict[str] = None
    username_warning: dict[str] = None
    morning_greeting: dict[str] = None
    afternoon_greeting: dict[str] = None
    evening_greeting: dict[str] = None
    night_greeting: dict[str] = None
    focus_agent_inscription: dict = None
    def __post_init__(self):
        with open(base_dir / "locales.json", "r") as f:
            data = json.load(f)
            self.gemini_api_warning = data["gemini_api_warning"]
            self.launch_message = data["launch_message"]
            self.username_warning = data["username_warning"]
            self.morning_greeting = data["morning_greeting"]
            self.afternoon_greeting = data["afternoon_greeting"]
            self.evening_greeting = data["evening_greeting"]
            self.night_greeting = data["night_greeting"]
            self.focus_agent_inscription = data["focus_agent_inscription"]


locales = Locales()

