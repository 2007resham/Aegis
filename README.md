# Cypher — Personal AI Assistant

A JARVIS-inspired personal assistant with voice interaction, persistent memory, real-time web search, system control, and hands-free wake-word activation — built from scratch in Python.

## Features

- 🧠 **Conversational brain** — powered by Google's Gemini API with function/tool calling
- 🗣️ **Voice in and out** — speech-to-text (local Whisper) and text-to-speech (Edge TTS)
- 👂 **Hands-free wake word** — custom-trained "Hey Cypher" detection via openWakeWord, no manual triggering needed
- 💾 **Persistent memory** — remembers facts across sessions (SQLite)
- 🔍 **Real-time web search** — via SerpAPI
- 💻 **System control** — open apps, run shell commands, open websites, browser search, read and search local files (with safety restrictions)
- 🚀 **Auto-start** — launches automatically at login, no manual startup required

## Tech Stack

- **Language:** Python 3.13
- **LLM:** Google Gemini (`gemini-3.5-flash-lite`)
- **Speech-to-text:** faster-whisper (local, no API cost)
- **Text-to-speech:** edge-tts (free, no API key)
- **Wake word:** openWakeWord (custom-trained model)
- **Search:** SerpAPI
- **Memory:** SQLite

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd cypher
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. Configure API keys

Copy `.env.example` to `.env` and fill in your keys:

GEMINI_API_KEY=your-gemini-key-here
SERPAPI_API_KEY=your-serpapi-key-here


- Gemini API key: [Google AI Studio](https://aistudio.google.com/apikey)
- SerpAPI key: [serpapi.com](https://serpapi.com/manage-api-key)

### 3. Get a wake-word model

This repo does **not** include a trained wake-word `.onnx` file (kept out of version control — see below). You'll need to train your own using [openWakeWord](https://github.com/dscripka/openWakeWord)'s training notebook, or point `voice/wake_word.py` at one of the built-in pretrained models (e.g., `"hey_jarvis"`) to test the pipeline first.

Place your trained `.onnx` file in the project root and update `WAKE_MODEL_NAME` in `voice/wake_word.py` to match.

### 4. Run it

```bash
python main.py
```

Say your wake word, wait for the acknowledgment beep, then talk normally.

## Project Structure

cypher/
├── main.py # Entry point — wake word loop, conversation flow
├── brain.py # Gemini API + tool-calling orchestration
├── config.py # Settings, API keys, system prompt
├── tools/
│ ├── memory.py # Long-term memory (SQLite)
│ ├── web_search.py # SerpAPI web search
│ └── system_control.py # App launching, commands, file access, browser control
├── voice/
│ ├── tts.py # Text-to-speech + audio cues
│ ├── stt.py # Speech-to-text (Whisper)
│ └── wake_word.py # Wake-word detection
├── requirements.txt
└── .env.example


## Known Limitations

- Wake-word detection accuracy depends on mic quality, input volume, and training data quality
- File reading is restricted to Desktop, Documents, and Downloads, and only supports plain text files (no PDF/Word parsing yet)
- Memory recall is keyword-based, not semantic
- No smart home integration yet (planned)

## Roadmap

- [ ] Smart home control (lights, fans) via Home Assistant
- [ ] PDF/Word document reading
- [ ] Streaming responses for lower latency
- [ ] Semantic memory search

## License

MIT (or update as you prefer)