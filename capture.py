import os
import subprocess
import time
from datetime import datetime

# Define where to save the images
IMAGE_DIR = os.path.expanduser("~/story_walker/capture")

def capture_image():
    """Triggers the camera hardware to capture a frame."""
    # Create a unique filename based on the current time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(IMAGE_DIR, f"scene_{timestamp}.jpg")
    
    print("\n[+] Initializing hardware capture...")
    
    # We use rpicam-still (the modern Pi camera command)
    # --width and --height shrink the image slightly to save processing time later
    cmd = [
        "rpicam-still",
        "-o", output_path,
        "--immediate",     # Skip the preview countdown
        "--width", "1280",
        "--height", "960",
        "-n"               # Do not show GUI preview
    ]
    
    try:
        # Run the command and suppress terminal spam
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if os.path.exists(output_path):
            print(f"[SUCCESS] Image saved to: {output_path}")
            return output_path
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Camera failed to capture: {e}")
        
    return None

def main():
    print("==============================================")
    print("  Scene Narrator: Phase 1 Active              ")
    print("==============================================")
    
    # Temporary Keyboard Trigger (Until your physical button arrives)
    try:
        while True:
            # Wait for the user to press Enter
            input("\nPress [ENTER] to capture an image (or CTRL+C to quit)...")
            capture_image()
            
    except KeyboardInterrupt:
        print("\n\n[-] Shutting down cleanly. Goodbye!")

if __name__ == "__main__":
    main()
