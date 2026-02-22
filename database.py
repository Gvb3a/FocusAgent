import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta


load_dotenv()
database_path = Path(__file__).parent / 'database.db'


# ██╗███╗   ██╗██╗████████╗██╗ █████╗ ██╗     ██╗███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# ██║████╗  ██║██║╚══██╔══╝██║██╔══██╗██║     ██║╚══███╔╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
# ██║██╔██╗ ██║██║   ██║   ██║███████║██║     ██║  ███╔╝ ███████║   ██║   ██║██║   ██║██╔██╗ ██║
# ██║██║╚██╗██║██║   ██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
# ██║██║ ╚████║██║   ██║   ██║██║  ██║███████╗██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
# ╚═╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                              


settings = [{
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
}, {
    'key': 'MEMORY',
    'description': 'Memory for agent)',
    'default': ''
}
]


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
    
    # TODO: time
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

    
    for setting in settings:
        cursor.execute('INSERT OR IGNORE INTO settings (key, value, description) VALUES (?, ?, ?)', 
                       (setting['key'], os.getenv(setting['key'], setting['default']), setting['description']))


    connection.commit()
    connection.close()



def str_to_datetime(value):
    """
    Ensure a datetime value is returned as a string in '%Y-%m-%d %H:%M:%S' format.
    Accepts a datetime or several common string formats.
    """
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            try:
                dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    dt = datetime.strptime(value, '%Y-%m-%d')
                except ValueError:
                    raise ValueError(f"Unrecognized datetime format: {value}")
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    raise TypeError('Datetime value must be a datetime or string')



#  █████╗  ██████╗████████╗██╗██╗   ██╗██╗████████╗██╗   ██╗
# ██╔══██╗██╔════╝╚══██╔══╝██║██║   ██║██║╚══██╔══╝╚██╗ ██╔╝
# ███████║██║        ██║   ██║██║   ██║██║   ██║    ╚████╔╝ 
# ██╔══██║██║        ██║   ██║╚██╗ ██╔╝██║   ██║     ╚██╔╝  
# ██║  ██║╚██████╗   ██║   ██║ ╚████╔╝ ██║   ██║      ██║   
# ╚═╝  ╚═╝ ╚═════╝   ╚═╝   ╚═╝  ╚═══╝  ╚═╝   ╚═╝      ╚═╝   



def create_activity(start_time, end_time, category, description):
    """
    Create a new activity
    
    Args:
        start_time: activity start time
        end_time: activity end time
        category: activity category
        description: activity description
    
    Returns:
        int: ID of created activity
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    start_str = str_to_datetime(start_time)
    end_str = str_to_datetime(end_time)

    cursor.execute('''
        INSERT INTO activities (start_time, end_time, category, description)
        VALUES (?, ?, ?, ?)
    ''', (start_str, end_str, category, description))

    activity_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return activity_id



def get_activities(limit=10, day_offset=0):
    """
    Get activities for a specific day
    
    Args:
        limit: number of activities to return
        day_offset: day offset (0 - today, -1 - yesterday, 1 - tomorrow)
    
    Returns:
        list: list of activity dictionaries
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    target_date = datetime.now() + timedelta(days=day_offset)
    start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    start_of_day_str = start_of_day.strftime('%Y-%m-%d %H:%M:%S')
    end_of_day_str = end_of_day.strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        SELECT id, start_time, end_time, category, description
        FROM activities
        WHERE start_time >= ? AND start_time <= ?
        ORDER BY start_time ASC
        LIMIT ?
    ''', (start_of_day_str, end_of_day_str, limit))
    
    rows = cursor.fetchall()
    connection.close()
    
    activities = []
    for row in rows:
        activities.append({
            'id': row[0],
            'start_time': row[1],
            'end_time': row[2],
            'category': row[3],
            'description': row[4]
        })
    
    return activities



def delete_activity(activity_id):
    """
    Delete activity by ID
    
    Args:
        activity_id: ID of activity to delete
    
    Returns:
        bool: True if deleted successfully, False if activity not found
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('DELETE FROM activities WHERE id = ?', (activity_id,))
    rows_affected = cursor.rowcount
    
    connection.commit()
    connection.close()
    
    return rows_affected > 0



# ███████╗██╗  ██╗███████╗██████╗  ██████╗██╗███████╗███████╗███████╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔══██╗██╔════╝██║██╔════╝██╔════╝██╔════╝
# █████╗   ╚███╔╝ █████╗  ██████╔╝██║     ██║███████╗█████╗  ███████╗
# ██╔══╝   ██╔██╗ ██╔══╝  ██╔══██╗██║     ██║╚════██║██╔══╝  ╚════██║
# ███████╗██╔╝ ██╗███████╗██║  ██║╚██████╗██║███████║███████╗███████║
# ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝╚══════╝╚══════╝╚══════╝
                                                                   


def get_all_exercises():
    """
    Get all exercises with their details
    
    Returns:
        list: list of exercise dictionaries
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT id, name, muscle_group, equipment, category
        FROM exercises
        ORDER BY id ASC
    ''')
    
    rows = cursor.fetchall()
    connection.close()
    
    exercises = []
    for row in rows:
        exercises.append({
            'id': row[0],
            'name': row[1],
            'muscle_group': row[2],
            'equipment': row[3],
            'category': row[4]
        })
    
    return exercises



def find_exercise(search_term):
    """
    Find exercise by name, equipment, or muscle group
    
    Args:
        search_term: term to search for
    
    Returns:
        list: list of matching exercise dictionaries
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    search_pattern = f"%{search_term.lower()}%"
    
    cursor.execute('''
        SELECT id, name, muscle_group, equipment, category
        FROM exercises
        WHERE LOWER(name) LIKE ? 
           OR LOWER(muscle_group) LIKE ?
           OR LOWER(equipment) LIKE ?
           OR LOWER(category) LIKE ?
        ORDER BY 
            CASE WHEN LOWER(name) LIKE ? THEN 1 ELSE 2 END,
            name ASC
    ''', (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
    
    rows = cursor.fetchall()
    connection.close()
    
    exercises = []
    for row in rows:
        exercises.append({
            'id': row[0],
            'name': row[1],
            'muscle_group': row[2],
            'equipment': row[3],
            'category': row[4]
        })
    
    return exercises



def create_exercise(name, muscle_group, equipment, category):
    """
    Create a new exercise
    
    Args:
        name: exercise name
        muscle_group: target muscle group
        equipment: required equipment
        category: exercise category
    
    Returns:
        int: ID of created exercise, or None if name already exists
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO exercises (name, muscle_group, equipment, category)
            VALUES (?, ?, ?, ?)
        ''', (name, muscle_group, equipment, category))
        
        exercise_id = cursor.lastrowid
        connection.commit()
        connection.close()
        
        return exercise_id
    except sqlite3.IntegrityError:
        connection.close()
        return None


def update_exercise(exercise_id, name=None, muscle_group=None, equipment=None, category=None):
    """
    Update an existing exercise record
    
    Args:
        exercise_id: ID of the exercise to update
        name: new exercise name (optional)
        muscle_group: new target muscle group (optional)
        equipment: new required equipment (optional)
        category: new exercise category (optional)
    
    Returns:
        bool: True if updated successfully, False if exercise not found or name conflict
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('SELECT id FROM exercises WHERE id = ?', (exercise_id,))
    if not cursor.fetchone():
        connection.close()
        return False
    
    fields = []
    values = []
    
    if name is not None:
        fields.append('name = ?')
        values.append(name)
    if muscle_group is not None:
        fields.append('muscle_group = ?')
        values.append(muscle_group)
    if equipment is not None:
        fields.append('equipment = ?')
        values.append(equipment)
    if category is not None:
        fields.append('category = ?')
        values.append(category)
    
    if fields:
        values.append(exercise_id)
        query = f'UPDATE exercises SET {", ".join(fields)} WHERE id = ?'
        
        try:
            cursor.execute(query, tuple(values))
            connection.commit()
            connection.close()
            return True
        except sqlite3.IntegrityError:
            connection.close()
            return False
    
    connection.close()
    return True


def delete_exercise(exercise_id):
    """
    Delete an exercise record by ID
    
    Args:
        exercise_id: ID of the exercise to delete
    
    Returns:
        bool: True if deleted successfully, False if not found
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('DELETE FROM exercises WHERE id = ?', (exercise_id,))
    deleted = cursor.rowcount > 0
    
    connection.commit()
    connection.close()
    
    return deleted



# ██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗ ██████╗ ██╗   ██╗████████╗
# ██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝██╔═══██╗██║   ██║╚══██╔══╝
# ██║ █╗ ██║██║   ██║██████╔╝█████╔╝ ██║   ██║██║   ██║   ██║   
# ██║███╗██║██║   ██║██╔══██╗██╔═██╗ ██║   ██║██║   ██║   ██║   
# ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗╚██████╔╝╚██████╔╝   ██║   
#  ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   
                                                              
def create_workout(exercise_id, sets, reps, weight=None):
    """
    Create a new workout record
    
    Args:
        exercise_id: ID of the exercise
        sets: number of sets
        reps: number of repetitions
        weight: weight used (optional)
    
    Returns:
        int: ID of created workout
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO workouts (exercise_id, sets, reps, weight)
        VALUES (?, ?, ?, ?)
    ''', (exercise_id, sets, reps, weight))
    
    workout_id = cursor.lastrowid
    connection.commit()
    connection.close()
    
    return workout_id


def get_workouts(day_offset=0):
    """
    Get workouts for a specific day
    
    Args:
        day_offset: day offset (0 - today, -1 - yesterday)
    
    Returns:
        list: list of workout dictionaries 
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    target_date = datetime.now() + timedelta(days=day_offset)
    start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    cursor.execute('''
        SELECT w.id, w.timestamp, w.exercise_id, w.sets, w.reps, w.weight, e.name
        FROM workouts w
        JOIN exercises e ON w.exercise_id = e.id
        WHERE w.timestamp >= ? AND w.timestamp <= ?
        ORDER BY w.timestamp ASC
    ''', (start_of_day, end_of_day))
    
    rows = cursor.fetchall()
    connection.close()
    
    workouts = []
    for row in rows:
        workouts.append({
            'id': row[0],
            'timestamp': row[1],
            'exercise_id': row[2],
            'sets': row[3],
            'reps': row[4],
            'weight': row[5],
            'exercise_name': row[6]
        })
    
    return workouts


def update_workout(workout_id, exercise_id=None, sets=None, reps=None, weight=None):
    """
    Update an existing workout record
    
    Args:
        workout_id: ID of the workout to update
        exercise_id: new exercise ID (optional)
        sets: new number of sets (optional)
        reps: new number of repetitions (optional)
        weight: new weight used (optional)
    
    Returns:
        bool: True if updated successfully, False if workout not found
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('SELECT id FROM workouts WHERE id = ?', (workout_id,))
    if not cursor.fetchone():
        connection.close()
        return False
    
    fields = []
    values = []
    
    if exercise_id is not None:
        fields.append('exercise_id = ?')
        values.append(exercise_id)
    if sets is not None:
        fields.append('sets = ?')
        values.append(sets)
    if reps is not None:
        fields.append('reps = ?')
        values.append(reps)
    if weight is not None:
        fields.append('weight = ?')
        values.append(weight)
    
    if fields:
        values.append(workout_id)
        query = f'UPDATE workouts SET {", ".join(fields)} WHERE id = ?'
        cursor.execute(query, tuple(values))
    
    connection.commit()
    connection.close()
    
    return True



def delete_workout(workout_id):
    """
    Delete a workout record by ID
    
    Args:
        workout_id: ID of the workout to delete
    
    Returns:
        bool: True if deleted successfully, False if not found
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('DELETE FROM workouts WHERE id = ?', (workout_id,))
    deleted = cursor.rowcount > 0
    
    connection.commit()
    connection.close()
    
    return deleted



# ███╗   ███╗ ██████╗ ███╗   ██╗██╗████████╗ ██████╗ ██████╗ ██╗███╗   ██╗ ██████╗ 
# ████╗ ████║██╔═══██╗████╗  ██║██║╚══██╔══╝██╔═══██╗██╔══██╗██║████╗  ██║██╔════╝ 
# ██╔████╔██║██║   ██║██╔██╗ ██║██║   ██║   ██║   ██║██████╔╝██║██╔██╗ ██║██║  ███╗
# ██║╚██╔╝██║██║   ██║██║╚██╗██║██║   ██║   ██║   ██║██╔══██╗██║██║╚██╗██║██║   ██║
# ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║██║   ██║   ╚██████╔╝██║  ██║██║██║ ╚████║╚██████╔╝
# ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
                                                                                 

def log_monitoring(windows_and_tabs):
    """
    Log monitoring data
    
    Args:
        windows_and_tabs: string with current windows and tabs info
    
    Returns:
        int: ID of created log entry
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO monitoring (windows_and_tabs)
        VALUES (?)
    ''', (windows_and_tabs,))
    
    log_id = cursor.lastrowid
    connection.commit()
    connection.close()
    
    return log_id



def get_monitoring_logs(hours_back=4, day_offset=0):
    """
    Get monitoring logs for a specific time period
    
    Args:
        hours_back: number of hours back from now to get logs
        day_offset: day offset (0 - today, -1 - yesterday, 1 - tomorrow)
    
    Returns:
        list: list of monitoring log dictionaries (sorted by timestamp ASC)
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    # Calculate time range
    target_date = datetime.now() + timedelta(days=day_offset)
    end_time = target_date
    start_time = target_date - timedelta(hours=hours_back)
    
    cursor.execute('''
        SELECT timestamp, windows_and_tabs
        FROM monitoring
        WHERE timestamp >= ? AND timestamp <= ?
        ORDER BY timestamp ASC
    ''', (start_time, end_time))
    
    rows = cursor.fetchall()
    connection.close()
    
    logs = []
    for row in rows:
        logs.append({
            'timestamp': row[0],
            'windows_and_tabs': row[1]
        })
    
    return logs



# ███████╗███████╗████████╗████████╗██╗███╗   ██╗ ██████╗ ███████╗
# ██╔════╝██╔════╝╚══██╔══╝╚══██╔══╝██║████╗  ██║██╔════╝ ██╔════╝
# ███████╗█████╗     ██║      ██║   ██║██╔██╗ ██║██║  ███╗███████╗
# ╚════██║██╔══╝     ██║      ██║   ██║██║╚██╗██║██║   ██║╚════██║
# ███████║███████╗   ██║      ██║   ██║██║ ╚████║╚██████╔╝███████║
# ╚══════╝╚══════╝   ╚═╝      ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝                          
                                         


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



def get_memory():
    """
    Get user memory/preferences
    
    Returns:
        str: user memory content or empty string
    """
    return get_setting('USER_MEMORY') or ""



def update_memory(content):
    """
    Replace entire memory with new content
    
    Args:
        content: new memory content
    
    Returns:
        bool: True if updated successfully
    """
    set_setting('USER_MEMORY', content, 'User preferences and memory')
    return True



def add_to_memory(content):
    """
    Append to existing memory
    
    Args:
        content: content to add to memory
    
    Returns:
        bool: True if added successfully
    """
    current = get_memory()
    new_memory = f"{current}\n{content}".strip()
    set_setting('USER_MEMORY', new_memory, 'User preferences and memory')
    return True



#  ██████╗ ██████╗ ███╗   ██╗██╗   ██╗███████╗██████╗ ███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# ██╔════╝██╔═══██╗████╗  ██║██║   ██║██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
# ██║     ██║   ██║██╔██╗ ██║██║   ██║█████╗  ██████╔╝███████╗███████║   ██║   ██║██║   ██║██╔██╗ ██║
# ██║     ██║   ██║██║╚██╗██║╚██╗ ██╔╝██╔══╝  ██╔══██╗╚════██║██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
# ╚██████╗╚██████╔╝██║ ╚████║ ╚████╔╝ ███████╗██║  ██║███████║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
#  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                                   


def save_message(role, content):
    """
    Save conversation message
    
    Args:
        role: message role ('user' or 'assistant')
        content: message content
    
    Returns:
        int: ID of created message
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO conversations (role, content)
        VALUES (?, ?)
    ''', (role, content))
    
    message_id = cursor.lastrowid
    connection.commit()
    connection.close()
    
    return message_id



def get_messages(limit=10):
    """
    Get recent conversation messages
    
    Args:
        limit: number of messages to return
    
    Returns:
        list: list of message dictionaries (sorted by timestamp DESC)
    """
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT timestamp, role, content
        FROM conversations
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    connection.close()
    
    messages = []
    for row in rows:
        messages.append({
            'timestamp': row[0],
            'role': row[1],
            'content': row[2]
        })
    
    return messages

init_database()