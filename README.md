# Story Walker
*An Edge-to-Cloud Accessible Scene Narrator built on Raspberry Pi.*

**Story Walker** is a wearable hardware project designed to translate complex visual surroundings into real-time audio descriptions for visually impaired users. It utilizes a physical hardware trigger to capture a scene, processes it through Google's Gemini 2.5 Flash multimodal AI, and returns a concise auditory description.

## ech Stack & Hardware
* **Edge Device:** Raspberry Pi 4B (4GB)
* **Vision Hardware:** Raspberry Pi Camera Module (CSI interface)
* **Cloud AI:** Google Gen AI SDK (Gemini 2.5 Flash)
* **Language:** Python 3 (subprocess, gpiozero, PIL)

## Current Milestone: Phase 2 Complete
- [x] **Phase 1:** Hardware trigger integration and local high-res image capture via `libcamera`.
- [x] **Phase 2:** Cloud inference integration. Securely passing edge frames to the Gemini 2.5 Flash API for accessibility-focused narration.
- [ ] **Phase 3:** Text-to-Speech (TTS) integration for local audio playback.
- [ ] **Phase 4:** System optimization, try-except networking fallbacks, and `systemd` daemon creation for headless operation.

