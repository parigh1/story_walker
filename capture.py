"""
capture.py
Main entry point. Runs the button-press loop:

  press Enter -> capture photo -> check internet -> describe scene ->
  speak each sentence as it's ready

This version includes TEMPORARY timing instrumentation for Phase 7
lag testing. Once we've gathered enough data, this gets reverted to
the clean version.
"""

import time

from modules.camera import capture_image
from modules.vision import narrate_scene
from modules.voice import speak_piper, speak_fallback
from modules.network import is_online


def main():
    print("Story Walker is ready.")
    print("Press Enter to describe your surroundings. Ctrl+C to quit.\n")

    while True:
        try:
            input()
        except KeyboardInterrupt:
            print("\nShutting down. Goodbye.")
            break

        t_start = time.time()

        speak_fallback("Looking now, please wait")
        t_after_feedback = time.time()

        image_path = capture_image()
        t_after_capture = time.time()

        if image_path is None:
            speak_fallback("Camera error. Please try again.")
            continue

        if not is_online():
            speak_fallback("No internet connection. Please check your hotspot.")
            continue
        t_after_network_check = time.time()

        first_sentence_spoken = False
        for sentence in narrate_scene(image_path):
            if not first_sentence_spoken:
                t_first_sentence = time.time()
                first_sentence_spoken = True
            speak_piper(sentence)
            t_sentence_end = time.time()
            print(f"  Sentence {sentence_count} spoke in {t_sentence_end - t_sentence_start:.2f}s: \"{sentence[:50]}...\"")

        # ---- Print the timing breakdown ----
        print("\n--- TIMING BREAKDOWN ---")
        print(f"Instant feedback spoken:     {t_after_feedback - t_start:.2f}s")
        print(f"Camera capture + preprocess: {t_after_capture - t_after_feedback:.2f}s")
        print(f"Network check:               {t_after_network_check - t_after_capture:.2f}s")
        if first_sentence_spoken:
            print(f"Time to first Gemini sentence: {t_first_sentence - t_after_network_check:.2f}s")
        print(f"Total time (button to done): {t_end - t_start:.2f}s")
        print("------------------------\n")


if __name__ == "__main__":
    main()