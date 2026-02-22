import platform
import subprocess
from datetime import datetime


def get_os():
    return platform.system()


def get_time():
    return datetime.now()


def get_time_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_all_windows():
    """Get all open windows with their titles"""
    os_name = get_os()
    
    if os_name == "Darwin":  # macOS
        script = '''
tell application "System Events"
    set appList to name of every application process whose visible is true
end tell

set output to ""
repeat with appName in appList
    set output to output & appName
    try
        tell application "System Events"
            tell process appName
                if exists window 1 then
                    set windowTitle to name of window 1
                    set output to output & ": " & windowTitle
                end if
            end tell
        end tell
    end try
    set output to output & " | "
end repeat

return output
'''
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else "Error"
    
    elif os_name == "Linux":
        result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            windows = []
            for line in result.stdout.strip().split('\n'):
                parts = line.split(None, 3)
                if len(parts) >= 4:
                    windows.append(parts[3])
            return " | ".join(windows) if windows else "No windows"
        return "Error"
    
    elif os_name == "Windows":
        script = 'Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | Select-Object MainWindowTitle | ForEach-Object {$_.MainWindowTitle}'
        result = subprocess.run(['powershell', '-Command', script], capture_output=True, text=True)
        windows = [w.strip() for w in result.stdout.strip().split('\n') if w.strip()]
        return " | ".join(windows) if windows else "No windows"
    
    return "Unsupported OS"


def get_current_window_title():
    """Get currently active window"""
    os_name = get_os()
    
    if os_name == "Darwin":  # macOS
        script = '''
tell application "System Events"
    set frontApp to name of first application process whose frontmost is true
    set frontWindow to ""
    try
        tell process frontApp
            set frontWindow to name of front window
        end tell
    end try
    return frontApp & ": " & frontWindow
end tell
'''
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else "Error"
    
    elif os_name == "Linux":
        result = subprocess.run(['xdotool', 'getactivewindow', 'getwindowname'], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else "Error"
    
    elif os_name == "Windows":
        script = 'Add-Type @"\nusing System;\nusing System.Runtime.InteropServices;\npublic class Win {\n[DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();\n[DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);\n}\n"@; $h = [Win]::GetForegroundWindow(); $s = New-Object System.Text.StringBuilder 256; [Win]::GetWindowText($h, $s, 256); $s.ToString()'
        result = subprocess.run(['powershell', '-Command', script], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else "Error"
    
    return "Unsupported OS"



def get_windows():
    """Get all windows with active window highlighted"""
    all_windows = get_all_windows()
    current_window = get_current_window_title()
    
    if 'Error' in (current_window, all_windows):
        return "Error retrieving windows"

    return all_windows.replace(current_window, f"*ACTIVE: {current_window}*")



def close_browser():
    """Close all browsers"""
    os_name = get_os()
    
    browsers = {
        "chrome": ["Google Chrome", "chrome", "chrome.exe"],
        "firefox": ["Firefox", "firefox", "firefox.exe"],
        "safari": ["Safari", "safari", None],
    }
    

    targets = []
    for names in browsers.values():
        targets.extend([n for n in names if n])

    if os_name == "Darwin":
        for target in targets:
            if target and not target.endswith('.exe'):
                subprocess.run(['osascript', '-e', f'quit app "{target}"'], check=False)
        return True
    elif os_name == "Linux":
        for target in targets:
            if target and not target.endswith('.exe'):
                subprocess.run(['pkill', '-f', target.lower()], check=False)
        return True
    elif os_name == "Windows":
        for target in targets:
            if target and target.endswith('.exe'):
                subprocess.run(['taskkill', '/F', '/IM', target], check=False)
        return True
    
    return False


def close_app(app_name):
    """Close any application by name"""
    os_name = get_os()
    
    if os_name == "Darwin":
        subprocess.run(['osascript', '-e', f'quit app "{app_name}"'], check=False)
        return True
    elif os_name == "Linux":
        subprocess.run(['pkill', '-f', app_name.lower()], check=False)
        return True
    elif os_name == "Windows":
        subprocess.run(['taskkill', '/F', '/IM', f'{app_name}.exe'], check=False)
        return True
    
    return False

