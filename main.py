import string
import time

from brain import start_chat, ask_aegis
from voice.tts import speak, play_beep
from voice.stt import listen
from voice.wake_word import wait_for_wake_word

EXIT_WORDS = {"exit", "quit", "shut down", "goodbye"}
SLEEP_WORDS = {"sleep", "go to sleep", "stand by", "sleep now"}


def handle_conversation_turn(chat, user_input: str) -> bool:
    print(f"You (voice): {user_input}")

    if not user_input.strip():
        print("Cypher: Didn't catch that, sir.\n")
        return True

    cleaned = user_input.lower().strip(string.punctuation + " ")
    if cleaned in EXIT_WORDS:
        print("Cypher: Goodbye, Resham.")
        speak("Goodbye, sir.")
        time.sleep(0.3)
        return False

    try:
        reply = ask_aegis(chat, user_input)
    except Exception as e:
        print(f"Cypher: Something went wrong — {e}")
        return True

    print(f"Cypher: {reply}\n")
    speak(reply)
    time.sleep(0.3)
    return True


def main():
    print("Cypher is online and listening for the wake word. Press Ctrl+C to quit.\n")
    chat = start_chat()

    try:
        while True:
            play_beep(frequency=440, duration=0.15)
            wait_for_wake_word()
            speak("Yes, sir?")
            time.sleep(0.3)

            while True:
                play_beep(frequency=880, duration=0.15)
                user_input = listen()

                if not user_input.strip():
                    print("[Cypher] No follow-up detected, back to wake word listening.\n")
                    time.sleep(0.5)
                    break

                cleaned = user_input.lower().strip(string.punctuation + " ")
                if cleaned in SLEEP_WORDS:
                    print("[Cypher] Sleep command received, going idle.\n")
                    speak("Going to sleep, sir.")
                    time.sleep(0.3)
                    break

                keep_going = handle_conversation_turn(chat, user_input)
                if not keep_going:
                    return
    except KeyboardInterrupt:
        print("\nCypher: Shutting down.")
if __name__ == "__main__":
    main()