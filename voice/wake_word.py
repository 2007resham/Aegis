import numpy as np
import sounddevice as sd
import openwakeword
from openwakeword.model import Model
from collections import deque

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280

WAKE_MODEL_NAME = "cypher"
DETECTION_THRESHOLD = 0.4

openwakeword.utils.download_models()
_model = Model(wakeword_models=["cypher.onnx"])


def wait_for_wake_word():
    print("[Cypher] Listening for wake word...")

    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16", blocksize=CHUNK_SIZE)
    stream.start()

    recent_scores = deque(maxlen=5)
    HITS_NEEDED_IN_WINDOW = 2

    try:
        while True:
            chunk, overflowed = stream.read(CHUNK_SIZE)
            if overflowed:
                print("[WARNING] Audio buffer overflowed — samples were dropped!")

            audio = chunk[:, 0]
            prediction = _model.predict(audio)

            score = prediction.get(WAKE_MODEL_NAME, 0)
            if score > 0.15:
                print(f"[debug] score: {score:.2f}")

            recent_scores.append(score > DETECTION_THRESHOLD)

            if sum(recent_scores) >= HITS_NEEDED_IN_WINDOW:
                print(f"[Cypher] Wake word detected! (score={score:.2f})")
                break
    finally:
        stream.stop()
        stream.close()