"""
network.py
One job: quickly check if we have internet before wasting time
trying to reach Gemini and failing.
"""

import socket
from config import NETWORK_CHECK_HOST, NETWORK_CHECK_PORT, NETWORK_TIMEOUT_SECONDS


def is_online() -> bool:
    """
    Tries to open a quick connection to a known reliable server.
    Returns True if online, False if not.
    This does NOT download anything -- just checks the door opens.
    """
    try:
        socket.setdefaulttimeout(NETWORK_TIMEOUT_SECONDS)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((NETWORK_CHECK_HOST, NETWORK_CHECK_PORT))
        sock.close()
        return True
    except OSError:
        return False


# Quick manual test -- run this file directly to check it works
if __name__ == "__main__":
    if is_online():
        print("✅ Internet connection detected.")
    else:
        print("❌ No internet connection.")