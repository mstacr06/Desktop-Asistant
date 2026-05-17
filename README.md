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

   
## 📅 Week 3: Core Assistant Mechanics & System Integration

This week marks a major milestone where the core architecture of the desktop assistant was established and primary commands for operating system interaction were implemented. 

> **Note:** To ensure a faster and error-free development cycle, all assistant responses are currently routed to **terminal (console) outputs**.

### 🚀 New Features

#### 🎙️ Speech-to-Text (STT) Processing
Integrated the `speech_recognition` library to convert live microphone input into processable string data, enabling hands-free interaction.

#### 🖥️ System & Conversation Commands
*   **Time & Date:** Implemented the `datetime` module to provide real-time local information.
*   **Social Interaction:** Added basic conversational capabilities such as greetings and small talk.

#### 🤖 App & Browser Automation
*   **Native Integration:** Utilized the `os` module to launch Windows applications like **Notepad**, **Calculator**, and **Spotify** without external dependencies.
*   **Web Navigation:** Implemented the `webbrowser` module to trigger the default browser for Google searches, YouTube, and custom media URLs.

#### ☁️ External API Integration (Weather Service)
*   Integrated the **OpenWeatherMap API** to provide real-time weather updates. 
*   The system parses city names from voice commands and fetches data using the `requests` module.

#### 🔐 Graceful Exit
Added secure termination triggers (e.g., "exit", "close", "stop") to stop the background infinite loop safely.

### 🛠️ Technologies & Dependencies

| Category | Tools / Libraries |
| :--- | :--- |
| **External Libraries** | `SpeechRecognition`, `PyAudio`, `requests` |
| **Standard Libraries** | `os`, `datetime`, `webbrowser`, `random`, `time` |
| **APIs** | OpenWeatherMap API |

---
## 📅 Week 4 Update: Advanced Automation & NLP Engine Upgrade

This week focused on making the assistant more autonomous, enhancing the text-to-speech quality, and completely overhauling the command recognition logic for better scalability.

### 🚀 New Features

#### 🧠 Dynamic Intent Recognition
Shifted the command recognition logic from static conditions to a dynamic, dictionary-based mapping system (`KOMUTLAR`). This allows the assistant to understand multiple phrasing variations for a single intent (e.g., mapping "aç", "başlat", and "çalıştır" all to the application launch function) seamlessly.

#### 🎙️ Continuous Listening & Wake Word
Implemented a background `listen_for_wake_word()` loop. The system now rests in a standby mode, actively listening for triggers like "hey asistan" before engaging the main interaction engine.

#### 🗣️ Voice Engine Overhaul
Upgraded the text-to-speech implementation by transitioning to `gTTS` (Google Text-to-Speech) combined with `playsound`. This provides a much higher-quality, natural-sounding Turkish voice response system, complete with automated temporary audio file management.

#### 🖥️ Advanced Desktop Automation
Integrated `pyautogui` to gain deeper system-level control without needing native Windows API calls:
*   **Audio Control:** Hardware-level simulation to mute, raise, or lower system volume.
*   **Screen Capture:** Automated screenshot functionality that saves images with unique timestamps.
*   **Dynamic App Launching:** Simulates keyboard presses (Windows key + typing) to search for and launch any application dynamically based on voice input.

#### 📚 Live Information & RSS Feeds
*   **Wikipedia API:** Added the ability to fetch, summarize, and dictate information on the fly, complete with error handling for disambiguation.
*   **News Integration:** Utilized `feedparser` to parse and read real-time breaking news headlines directly from the TRT Haber RSS feed.

### 🛠️ Technologies & Dependencies

| Category | Tools / Libraries |
| :--- | :--- |
| **External Libraries** | `SpeechRecognition`, `gTTS`, `playsound`, `wikipedia`, `pyautogui`, `feedparser`, `requests` |
| **Standard Libraries** | `os`, `datetime`, `random`, `time` |
| **APIs & Feeds** | OpenWeatherMap API, TRT Haber RSS, Google Web Speech API |

---





