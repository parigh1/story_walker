"""
config.py
All project settings live here. Change values in this ONE file
instead of hunting through every module.
"""

import os
from dotenv import load_dotenv

# Load variables from .env into the environment
load_dotenv()

# This finds the project root folder (where config.py itself lives),
# no matter which folder the script is actually launched from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- API ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"
TEMPERATURE = 0.2          # lower = more literal, less "creative" (reduces hallucination)

# ---- Camera / Image ----
CAPTURE_DIR = os.path.join(BASE_DIR, "captures")
IMAGE_MAX_WIDTH = 800       # resize target before sending to Gemini

# ---- Voice ----
PIPER_VOICE_PATH = os.path.join(BASE_DIR, "voices", "en_US-amy-medium.onnx")
ESPEAK_VOICE = "en+f3"      # your old fallback voice setting
ESPEAK_SPEED = 150

# ---- Network ----
NETWORK_CHECK_HOST = "8.8.8.8"   # Google DNS, fast + reliable to ping
NETWORK_CHECK_PORT = 53
NETWORK_TIMEOUT_SECONDS = 2

# ---- Misc ----
LOG_DIR = os.path.join(BASE_DIR, "logs")