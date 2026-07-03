"""
vision.py
Handles all communication with Gemini for scene description.

narrate_scene() is a GENERATOR -- instead of returning one big block of
text, it yields complete sentences one at a time, as Gemini streams them
back. This lets the calling code (capture.py) start speaking the first
sentence while Gemini is still generating the rest, which is the main
fix for the lag you noticed.
"""

from google import genai
from google.genai import types
from PIL import Image

from config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE

_client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are a mobility assistant for a visually impaired person.
Describe only what is clearly and directly visible in this image.
Do not guess, infer, or mention objects that might typically be present
but are not actually visible in the frame.
Keep the description to 2-3 short, direct sentences.
Focus on: obstacles, pathways, doors, stairs, and anything relevant
to safely moving through this space.
If the image is too dark, blurry, or unclear to describe confidently,
say so directly instead of guessing."""


def narrate_scene(image_path: str):
    """
    Sends an image to Gemini and yields complete sentences as they
    stream back. This is a generator -- use it with a for loop.
    """
    try:
        image = Image.open(image_path)

        response_stream = _client.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=[SYSTEM_PROMPT, image],
            config=types.GenerateContentConfig(
                temperature=TEMPERATURE,
            ),
        )

        buffer = ""
        for chunk in response_stream:
            if not chunk.text:
                continue
            buffer += chunk.text

            # Check if we've completed one or more sentences
            while True:
                sentence, buffer, found = _extract_sentence(buffer)
                if not found:
                    break
                yield sentence

        # Yield whatever's left over after the stream ends
        leftover = buffer.strip()
        if leftover:
            yield leftover

    except Exception as e:
        yield f"Sorry, I had trouble describing that. Error: {e}"


def _extract_sentence(buffer: str):
    """
    Looks for the first sentence-ending punctuation in the buffer.
    Returns (sentence, remaining_buffer, found_bool).
    """
    for punct in [". ", "! ", "? ", ".\n", "!\n", "?\n"]:
        idx = buffer.find(punct)
        if idx != -1:
            sentence = buffer[: idx + 1].strip()
            remaining = buffer[idx + len(punct):]
            return sentence, remaining, True
    return buffer, buffer, False


# Quick manual test -- run this file directly
if __name__ == "__main__":
    test_image_path = "../captures/test_image.jpg"

    print("Streaming description from Gemini:\n")
    for sentence in narrate_scene(test_image_path):
        print(f"-> {sentence}")