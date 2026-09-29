from google import genai
from google.genai import types

import config
from tools.web_search import web_search
from tools.memory import remember, recall
from tools.system_control import open_app, run_command
from tools.system_control import open_app, run_command, open_website, browser_search, read_file, search_files

_client = genai.Client(api_key=config.GEMINI_API_KEY)


def start_chat():
    """Starts a new Aegis conversation with automatic tool calling enabled."""
    return _client.chats.create(
        model=config.MODEL,
        config=types.GenerateContentConfig(
            system_instruction=config.SYSTEM_PROMPT,
            tools=[web_search, remember, recall, open_app, run_command, open_website, browser_search, read_file, search_files],
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        ),
    )


def ask_aegis(chat, user_message: str) -> str:
    """Sends a message to Aegis and returns its final text reply."""
    response = chat.send_message(user_message)
    return response.text