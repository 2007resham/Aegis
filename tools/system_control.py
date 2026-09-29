import webbrowser
import os
import platform
import subprocess

# Common app name -> launch command per OS. Add your own frequently used apps here.
APP_MAP = {
    "windows": {
        "notepad": "notepad",
        "calculator": "calc",
        "chrome": "start chrome",
        "vscode": "code",
        "explorer": "explorer",
    },
    "linux": {
        "calculator": "gnome-calculator",
        "chrome": "google-chrome",
        "vscode": "code",
        "files": "nautilus",
    },
    "darwin": {  # macOS
        "calculator": "open -a Calculator",
        "chrome": "open -a 'Google Chrome'",
        "vscode": "open -a 'Visual Studio Code'",
        "finder": "open -a Finder",
    },
}


def open_app(app_name: str) -> str:
    """Open an application by name (see APP_MAP for known apps per OS)."""
    system = platform.system().lower()
    apps = APP_MAP.get(system, {})
    key = app_name.strip().lower()

    if key not in apps:
        return (
            f"'{app_name}' isn't in the known app list for {system}. "
            f"Known apps: {', '.join(apps.keys()) or 'none configured'}. "
            f"Add it to APP_MAP in tools/system_control.py."
        )

    try:
        subprocess.Popen(apps[key], shell=True)
        return f"Opening {app_name}."
    except Exception as e:
        return f"Failed to open {app_name}: {e}"


# Commands blocked outright for safety, regardless of context.
BLOCKED_SUBSTRINGS = ["rm -rf", "format ", "del /f", "shutdown", "diskpart", "mkfs"]


def run_command(command: str) -> str:
    """Run a shell command and return its output. Blocks known-dangerous commands."""
    lowered = command.lower()
    if any(bad in lowered for bad in BLOCKED_SUBSTRINGS):
        return f"Refused to run '{command}' — matches a blocked pattern for safety."

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = (result.stdout or "") + (result.stderr or "")
        return output.strip()[:2000] or "(command ran with no output)"
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds."
    except Exception as e:
        return f"Failed to run command: {e}"

def open_website(url: str) -> str:
    """Opens a specific website in the default browser."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        webbrowser.open(url)
        return f"Opened {url}."
    except Exception as e:
        return f"Failed to open {url}: {e}"


def browser_search(query: str) -> str:
    """Opens the default browser with a Google search for the given query."""
    try:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searched for '{query}' in the browser."
    except Exception as e:
        return f"Failed to search: {e}"


# Only files under these folders can be accessed — keeps this from becoming
# a way to read anything anywhere on the system without limits.
ALLOWED_READ_DIRS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
]
MAX_FILE_READ_CHARS = 5000


def read_file(path: str) -> str:
    """Reads and returns the text content of a file, if it's in an allowed folder."""
    full_path = os.path.abspath(os.path.expanduser(path))

    if not any(full_path.startswith(os.path.abspath(d)) for d in ALLOWED_READ_DIRS):
        return (
            f"Refused to read '{path}' — only files under Desktop, Documents, "
            f"or Downloads can be read for safety."
        )

    if not os.path.isfile(full_path):
        return f"File not found: {path}"

    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(MAX_FILE_READ_CHARS)
        return content if content else "(file is empty)"
    except Exception as e:
        return f"Failed to read file: {e}"


def search_files(keyword: str, max_results: int = 10) -> str:
    """Searches Desktop, Documents, and Downloads for filenames containing the keyword."""
    keyword_lower = keyword.lower()
    matches = []

    for base_dir in ALLOWED_READ_DIRS:
        if not os.path.isdir(base_dir):
            continue
        for root, _, files in os.walk(base_dir):
            for fname in files:
                if keyword_lower in fname.lower():
                    matches.append(os.path.join(root, fname))
                    if len(matches) >= max_results:
                        break
            if len(matches) >= max_results:
                break
        if len(matches) >= max_results:
            break

    if not matches:
        return f"No files found matching '{keyword}' in Desktop, Documents, or Downloads."

    return "\n".join(matches)