import asyncio
import os
import tempfile
import time

import numpy as np
import edge_tts
from playsound import playsound
from scipy.io.wavfile import write as write_wav

VOICE = "en-GB-RyanNeural"
RATE = "-5%"
PITCH = "-15Hz"  # lower pitch to compensate for the voice sounding lighter now


async def _generate_speech(text: str, output_path: str):
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(output_path)


def speak(text: str):
    """Converts text to speech and plays it out loud."""
    if not text or not text.strip():
        return

    print(f"[Cypher speaking]: {text}")

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        asyncio.run(_generate_speech(text, tmp_path))
        playsound(tmp_path)
    except Exception as e:
        print(f"[Cypher] TTS playback error: {e}")
    finally:
        time.sleep(0.1)
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except PermissionError:
            pass


def play_beep(frequency: int = 880, duration: float = 0.15):
    """Plays a short, instant beep — used to signal state changes without network delay."""
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(frequency * 2 * np.pi * t)
    audio = (tone * 32767 * 0.3).astype(np.int16)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        write_wav(tmp_path, sample_rate, audio)
        playsound(tmp_path)
    except Exception as e:
        print(f"[Cypher] Beep playback error: {e}")
    finally:
        time.sleep(0.1)
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except PermissionError:
            pass