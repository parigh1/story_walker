"""
capture.py
Main entry point. Runs the button-press loop:

  press Enter -> capture photo -> check internet -> describe scene ->
  speak each sentence as it's ready

This file stays intentionally small -- all the real logic lives in
modules/camera.py, modules/vision.py, modules/voice.py, modules/network.py.
"""

from modules.camera import capture_image
from modules.vision import narrate_scene
from modules.voice import speak_piper, speak_fallback
from modules.network import is_online


def main():
    print("Story Walker is ready.")
    print("Press Enter to describe your surroundings. Ctrl+C to quit.\n")

    while True:
        try:
            input()  # wait for Enter key press
        except KeyboardInterrupt:
            print("\nShutting down. Goodbye.")
            break

        # Instant feedback so the user knows the button press registered
        speak_fallback("Looking now, please wait")

        # Step 1: capture + process the photo
        image_path = capture_image()
        if image_path is None:
            speak_fallback("Camera error. Please try again.")
            continue

        # Step 2: check internet before wasting time on a doomed API call
        if not is_online():
            speak_fallback("No internet connection. Please check your hotspot.")
            continue

        # Step 3: stream the description and speak each sentence as it arrives
        for sentence in narrate_scene(image_path):
            speak_piper(sentence)


if __name__ == "__main__":
    main()