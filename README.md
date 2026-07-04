# Story Walker

Story Walker is a wearable assistive device that describes the world out loud. Point the camera, press a button, and hear a short, plain-language description of what's in front of you — obstacles, doors, pathways, anything relevant to moving through a space safely. It's built for visually impaired users, runs on a Raspberry Pi, and doesn't cost anything to operate.

I started this project because most "AI vision assistant" builds I found online either needed expensive hardware, relied on paid APIs, or fell apart the moment lighting wasn't perfect. Story Walker is my attempt at something that actually holds up outside a demo video — cheap to build, free to run, and honest when it can't see clearly instead of guessing.

## How it works

The pipeline is deliberately simple: capture, describe, speak.

1. User presses Enter (or a wired button, eventually)
2. The Pi Camera takes a photo
3. The photo gets resized and brightness-corrected on-device before it goes anywhere
4. The image is sent to Gemini 2.5 Flash, which returns a short, literal description
5. The description is read aloud through Piper, a natural-sounding offline TTS engine

If the camera fails, the internet drops, or the API call errors out, the device says so immediately instead of going silent. For something someone is relying on to navigate, silence is worse than an error message.

## Why these tools specifically

**Gemini 2.5 Flash** for the vision model — fast enough for near-real-time use, and the free tier is generous enough for a personal project like this. The prompt is written to explicitly discourage the model from inferring objects it can't actually see, since early testing showed vision models will sometimes describe things that "belong" in a scene rather than things that are there.

**Piper** for text-to-speech, replacing the espeak voice I started with. Piper runs entirely offline on the Pi's CPU, sounds like an actual person instead of a 1990s GPS unit, and is fast enough not to add noticeable delay. espeak is still in the codebase as a fallback — it has almost no startup delay, which makes it better suited for quick status messages ("no internet," "camera error") than for full scene narration.

**OpenCV (CLAHE)** for a quick brightness/contrast pass on every photo before it's sent off. This came directly out of researching similar projects — several ran into accuracy problems specifically in low-light conditions, so correcting for that locally, before the image ever leaves the device, seemed worth the few extra lines of code.

Everything here is free. No paid API tiers, no subscriptions, no cloud hosting costs. The only real expense is the hardware itself.

## Project layout

```
story_walker/
├── capture.py           Main loop — waits for input, runs the pipeline
├── config.py             All settings in one place
├── modules/
│   ├── camera.py          Photo capture, resizing, brightness correction
│   ├── vision.py           Talks to Gemini, streams the response back
│   ├── voice.py             Piper TTS, with espeak as a fallback
│   └── network.py            Quick connectivity check before calling the API
├── voices/                Piper voice files (not committed — see setup)
├── captures/               Saved photos (not committed)
└── requirements.txt
```

I split it this way mostly for my own sanity. The original version of this project was a single ~90-line script, which was fine until I started adding streaming responses, image preprocessing, and fallback logic — at that point, everything living in one file was starting to get hard to reason about.

## Getting it running

Clone the repo and set up a virtual environment:

```bash
git clone https://github.com/parigh1/story_walker.git
cd story_walker
python3 -m venv venv
source venv/bin/activate       # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

You'll need a Gemini API key ([Google AI Studio](https://aistudio.google.com), free tier works fine). Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
```

Download a Piper voice model — I'm using `en_US-amy-medium`, available from the [Piper voices repo on Hugging Face](https://huggingface.co/rhasspy/piper-voices). Drop both the `.onnx` and `.onnx.json` files into `voices/`.

On the Raspberry Pi specifically, you'll also need a few system packages that aren't installed through pip:

```bash
sudo apt install espeak-ng alsa-utils libcamera-apps -y
```

Then just run it:

```bash
python capture.py
```

Press Enter, and it'll capture, describe, and speak.

## Where this is at

- [x] Rebuilt from a single-file script into a proper modular structure
- [x] Swapped espeak for Piper as the primary voice
- [x] Gemini responses now stream in rather than blocking on the full reply
- [x] Prompt tuned to reduce hallucinated objects, temperature lowered for more literal output
- [x] Images are resized and contrast-corrected before upload — cut description time noticeably in testing
- [x] Full pipeline wired together and working end-to-end on desktop
- [ ] Deployed and tested on the actual Raspberry Pi hardware
- [ ] Real-world latency and thermal testing
- [ ] Offline text reading (OCR), GPS context, and other feature work down the line

## A few notes on design decisions

**The device should never go silent.** Every point of failure I could think of — no camera, no internet, API timeout — has a spoken response. A blind user staring at a black screen has no idea anything went wrong; a blind user hearing "no internet connection" at least knows what to check.

**Accuracy matters more than eloquence here.** This isn't a captioning tool trying to write something impressive — it's meant to be trusted. That shaped a lot of the prompt engineering and the decision to lower the model's temperature: a slightly duller but more literal description beats a vivid but partially made-up one.

**Everything runs on hardware a hobbyist can actually afford.** A Raspberry Pi 4B, a camera module, and a pair of headphones. No dedicated GPU, no subscription fees.

## Hardware used

- Raspberry Pi 4B (4GB)
- Raspberry Pi Camera Module
- Headphones or a Bluetooth speaker
- A phone hotspot or USB tethering for internet on the go

## License

MIT
