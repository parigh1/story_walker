"""
voice.py
Handles all text-to-speech output.

speak_piper()    -> primary voice, natural sounding, used for normal narration
speak_fallback() -> old espeak voice, near-zero startup delay, used only for
                     quick error/status messages where speed matters more
                     than voice quality

NOTE: We use Piper's Python API directly (piper.PiperVoice) instead of
shelling out to the `piper` command line tool. The CLI in piper-tts 1.4.x
tries to look up voices through its own download/registry system, which
caused "Unable to find voice" errors even when the files existed locally.
Loading the .onnx file directly through the Python API avoids that entirely.
"""

import subprocess
import wave
import os
import platform

from config import PIPER_VOICE_PATH, ESPEAK_VOICE, ESPEAK_SPEED

# Load the Piper voice ONCE when this module is imported, not on every
# speak_piper() call -- loading the model has real startup cost, and we
# don't want to pay it every single time someone presses the button.
_piper_voice = None


def _get_piper_voice():
    global _piper_voice
    if _piper_voice is None:
        from piper import PiperVoice
        _piper_voice = PiperVoice.load(PIPER_VOICE_PATH)
    return _piper_voice


def speak_piper(text: str) -> None:
    """
    Converts text to speech using Piper and plays it.
    Works on both Windows (laptop testing) and Linux (Raspberry Pi).
    """
    if not text.strip():
        return

    temp_wav_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "logs", "_temp_speech.wav"
    )
    temp_wav_path = os.path.abspath(temp_wav_path)

    try:
        voice = _get_piper_voice()

        with wave.open(temp_wav_path, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)

        _play_wav(temp_wav_path)

    except Exception as e:
        print(f"[voice.py] Piper failed, falling back to espeak. Error: {e}")
        speak_fallback(text)

    finally:
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)


def _play_wav(path: str) -> None:
    """
    Plays a wav file. Linux (Pi) uses aplay. Windows (laptop) uses winsound.
    This is the ONE function that needs to change between laptop and Pi --
    everything else in this file stays identical on both.
    """
    system = platform.system()

    if system == "Windows":
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME)
    else:
        # Linux / Raspberry Pi
        subprocess.run(["aplay", path], check=True,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def speak_fallback(text: str) -> None:
    """
    Old espeak voice. Fast, robotic, but has near-zero startup delay.
    Used for network errors and quick status messages, NOT normal narration.
    On Windows this will simply fail quietly since espeak-ng isn't installed
    there by default -- that's expected, this path is really for the Pi.
    """
    try:
        subprocess.run(
            ["espeak-ng", "-v", ESPEAK_VOICE, "-s", str(ESPEAK_SPEED), text],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # On laptop this is expected if espeak-ng isn't installed.
        # We just print instead of crashing, so testing isn't blocked.
        print(f"[voice.py] espeak-ng not available. Message was: {text}")


# Quick manual test -- run this file directly
if __name__ == "__main__":
    print("Testing speak_piper()...")
    speak_piper("This is a test of the Piper voice system.")

    print("Testing speak_fallback()...")
    speak_fallback("This is a test of the fallback voice.")