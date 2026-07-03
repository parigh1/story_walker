"""
camera.py
Handles taking photos and preparing them before they're sent to Gemini.

capture_image() is the main entry point -- on the Raspberry Pi it fires
rpicam-still to take a real photo. On a laptop (no camera hardware), it
falls back to using an existing test image so the rest of the pipeline
can still be developed and tested.

Every captured image is automatically resized and brightness-corrected
before the file path is returned -- this matches what we already proved
in Phase 3 testing (a full-size 4032x3024 photo took 9s to describe,
resizing to 800px brought that down to 5-7s).
"""

import subprocess
import platform
import os
from datetime import datetime

import cv2
from PIL import Image

from config import CAPTURE_DIR, IMAGE_MAX_WIDTH


def capture_image() -> str | None:
    """
    Takes a photo and returns the path to a resized, brightness-corrected
    version ready to send to Gemini. Returns None if capture fails.
    """
    raw_path = _take_photo()
    if raw_path is None:
        return None

    _resize_image(raw_path)
    _fix_brightness(raw_path)

    return raw_path


def _take_photo() -> str | None:
    """
    Takes the actual photo. Uses rpicam-still on the Pi (Linux).
    On Windows (laptop testing), there's no camera hardware, so this
    copies the existing test image instead -- lets you test the rest
    of the pipeline without needing a Pi.
    """
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(CAPTURE_DIR, f"capture_{timestamp}.jpg")

    if platform.system() == "Windows":
        # Laptop testing fallback -- no real camera available
        sample_path = os.path.join(CAPTURE_DIR, "test_image.jpg")
        if not os.path.exists(sample_path):
            print(f"[camera.py] No test image found at {sample_path}")
            return None

        import shutil
        shutil.copy(sample_path, output_path)
        print(f"[camera.py] (Laptop mode) Used test image -> {output_path}")
        return output_path

    else:
        # Real Raspberry Pi capture
        try:
            subprocess.run(
                [
                    "rpicam-still",
                    "-o", output_path,
                    "--width", "1280",
                    "--height", "960",
                    "--immediate",
                    "-n",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return output_path
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"[camera.py] Camera capture failed: {e}")
            return None


def _resize_image(image_path: str) -> None:
    """
    Resizes the image in-place so the longer side matches IMAGE_MAX_WIDTH.
    Smaller upload = faster Gemini response (proven in Phase 3 testing).
    """
    img = Image.open(image_path)

    if img.width <= IMAGE_MAX_WIDTH:
        return  # already small enough, don't upscale

    ratio = IMAGE_MAX_WIDTH / img.width
    new_height = int(img.height * ratio)
    resized = img.resize((IMAGE_MAX_WIDTH, new_height))
    resized.save(image_path, quality=85)


def _fix_brightness(image_path: str) -> None:
    """
    Applies CLAHE (adaptive contrast/brightness correction) to the image.
    This targets the lighting-hallucination problem: research showed
    Gemini Vision is more likely to hallucinate objects in poorly-lit
    images. Boosting local contrast before sending helps Gemini "see"
    the scene more clearly.
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"[camera.py] Could not read image for brightness fix: {image_path}")
        return

    # Convert to LAB color space -- CLAHE works on the lightness channel only,
    # so colors aren't distorted, just brightness/contrast.
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_corrected = clahe.apply(l_channel)

    corrected_lab = cv2.merge((l_corrected, a_channel, b_channel))
    corrected_bgr = cv2.cvtColor(corrected_lab, cv2.COLOR_LAB2BGR)

    cv2.imwrite(image_path, corrected_bgr)


# Quick manual test -- run this file directly
if __name__ == "__main__":
    print("Testing capture_image()...")
    result = capture_image()

    if result:
        print(f"Success! Processed image saved at: {result}")
        img = Image.open(result)
        print(f"Final image size: {img.size}")
    else:
        print("Capture failed.")