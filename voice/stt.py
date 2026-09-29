import os


import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as write_wav
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
TEMP_WAV = "temp_recording.wav"

_model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=8, num_workers=1)
# Tune these if it cuts you off too early or listens too long
SILENCE_THRESHOLD = 400        # amplitude below this counts as "quiet"
SILENCE_DURATION = 0.9         # seconds of quiet before it decides you're done
MAX_DURATION = 30              # hard cap so it never listens forever
CHUNK_DURATION = 0.1           # how often we check the audio level (seconds)


def record_until_silence() -> str:
    """Records from the mic, starting immediately and stopping automatically
    once it detects `SILENCE_DURATION` seconds of quiet after you've spoken."""
    print("[Cypher] Listening...")

    chunk_samples = int(CHUNK_DURATION * SAMPLE_RATE)
    silence_chunks_needed = int(SILENCE_DURATION / CHUNK_DURATION)
    max_chunks = int(MAX_DURATION / CHUNK_DURATION)

    recorded = []
    silent_chunk_count = 0
    has_spoken = False

    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    stream.start()

    for _ in range(max_chunks):
        chunk, _ = stream.read(chunk_samples)
        recorded.append(chunk)

        amplitude = np.abs(chunk).max()
        print(f"[debug amplitude] {amplitude}")  # add this line
        if amplitude > SILENCE_THRESHOLD:
            has_spoken = True
            silent_chunk_count = 0
        elif has_spoken:
            silent_chunk_count += 1
            if silent_chunk_count >= silence_chunks_needed:
                break

    stream.stop()
    stream.close()
    print("[Cypher] Done listening.")

    audio = np.concatenate(recorded, axis=0)
    write_wav(TEMP_WAV, SAMPLE_RATE, audio)
    return TEMP_WAV


def transcribe(audio_path: str) -> str:
    """Transcribes a WAV file to text, filtering out likely hallucinations on silence."""
    segments, _ = _model.transcribe(
        audio_path,
        language="en",
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
        condition_on_previous_text=False,
        beam_size=5,
    )

    real_segments = []
    for seg in segments:
        # High no_speech_prob or very low confidence usually means Whisper
        # is hallucinating on silence/noise rather than transcribing real speech
        if seg.no_speech_prob > 0.6 or seg.avg_logprob < -1.0:
            continue
        real_segments.append(seg.text.strip())

    return " ".join(real_segments).strip()


def listen() -> str:
    """Records until silence, transcribes it, then deletes the recording."""
    audio_path = record_until_silence()
    try:
        text = transcribe(audio_path)
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
    return text