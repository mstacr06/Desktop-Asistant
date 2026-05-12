# Desktop-Asistant
The project for Advanced Programming presentation.
# Voice Assistant Project - Week 2 Progress 🚀

This repository tracks the weekly development of a Python-based voice recognition assistant.

## 📅 Week 2 Update: Core Engine Development
In the second week of the project, I focused on building the core speech recognition engine and establishing a stable "Demo Mode" for testing.

### Key Deliverables:
- **Speech-to-Text Integration:** Successfully integrated the `SpeechRecognition` library with Google's Web Speech API.
- **Microphone Calibration:** Added an ambient noise adjustment feature to ensure the assistant works in different environments (like classrooms or offices).
- **Intent Recognition:** Developed a basic logic to identify commands like "open", "run", "hello", and "stop".
- **Silent Feedback System:** Implemented a terminal-based feedback loop. The assistant currently "responds" via text to ensure stability during the initial testing phase.

## 🛠️ Technical Stack (Current)
- **Language:** Python 3.x
- **Libraries:** `SpeechRecognition`, `Pyttsx3`, `PyAudio`

## ⚙️ How to Run
1. Install dependencies:
   ```bash
   pip install speechrecognition pyttsx3 pyaudio
