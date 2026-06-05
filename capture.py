import os
import subprocess
from datetime import datetime
from PIL import Image
from google import genai

IMAGE_DIR = os.path.expanduser("~/story_walker/capture")

# The client automatically picks up the GEMINI_API_KEY you saved in Step 2
client = genai.Client()

def capture_image():
    """Triggers the camera hardware to capture a frame."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(IMAGE_DIR, f"scene_{timestamp}.jpg")
    
    print("\n[+] Capturing scene...")
    cmd = [
        "rpicam-still",
        "-o", output_path,
        "--immediate",
        "--width", "1280",
        "--height", "960",
        "-n"
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Camera failed to capture: {e}")
        return None

def narrate_scene(image_path):
    """Sends the captured image to Gemini 2.5 Flash for analysis."""
    print("[+] Sending image to Gemini 2.5 Flash...")
    try:
        # Load the local image
        img = Image.open(image_path)
        
        # The prompt forces the model to act as a visual aid
        prompt = "You are a visual assistant for a visually impaired person. Describe the main subjects and layout of this scene in 2-3 short, clear sentences. Be direct and objective."
        
        # Make the API call
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img]
        )
        
        print("\n=== SCENE DESCRIPTION ===")
        print(response.text)
        print("=========================\n")
        
    except Exception as e:
        print(f"[ERROR] API Request failed. Check your network or API key. Error: {e}")

def main():
    print("==============================================")
    print("  Story Walker: Phase 2 Active                ")
    print("==============================================")
    
    try:
        while True:
            input("\nPress [ENTER] to capture and analyze an image (or CTRL+C to quit)...")
            
            image_path = capture_image()
            if image_path:
                narrate_scene(image_path)
                
    except KeyboardInterrupt:
        print("\n\n[-] Shutting down cleanly. Goodbye!")

if __name__ == "__main__":
    main()
