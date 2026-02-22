import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from system_api import get_time, get_time_str


load_dotenv()
database_path = Path(__file__).parent / 'database.db'
env_settings = [{
    'key': 'GEMINI_API_KEY',
    'description': 'API key for Google Gemini LLM',
    'default': ''
}, {
    'key': 'GEMINI_MODEL',
    'description': 'Default model for Google Gemini LLM',
    'default': 'gemini-2.5-flash'
}, {
    'key': 'LANGUAGE',
    'description': 'User interface language (en, ru)',
    'default': 'en'
}]



def init_database():
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            muscle_group TEXT,
            equipment TEXT,
            category TEXT
        )
    ''')
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            exercise_id INTEGER NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        )
    ''')
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitoring (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            windows_and_tabs TEXT
        )
    ''')
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT
        )
    ''')

    
    for setting in env_settings:
        cursor.execute('INSERT OR IGNORE INTO settings (key, value, description) VALUES (?, ?, ?)', 
                       (setting['key'], os.getenv(setting['key'], setting['default']), setting['description']))


    connection.commit()
    connection.close()



def get_env_settings():
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.execute('SELECT key, value FROM settings')
    settings = {row[0]: row[1] for row in cursor.fetchall()}
    connection.close()
    return settings



def get_setting(key):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    result = cursor.fetchone()
    
    connection.close()
    return result[0] if result else None


def set_setting(key, value, description=None):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('''INSERT OR REPLACE INTO settings (key, value, description) VALUES (?, ?, ?)''', (key, value, description))
    
    connection.commit()
    connection.close()
    return True


init_database()