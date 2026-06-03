# 🎙️ Desktop-Assistant
> The project for Advanced Programming presentation.

![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

This repository tracks the weekly development of a Python-based voice recognition assistant.

---

## 📅 Week 2 Update: Core Engine Development
In the second week of the project, I focused on building the core speech recognition engine and establishing a stable "Demo Mode" for testing.

### Key Deliverables:
*   **Speech-to-Text Integration:** Successfully integrated the `SpeechRecognition` library with Google's Web Speech API.
*   **Microphone Calibration:** Added an ambient noise adjustment feature to ensure the assistant works in different environments (like classrooms or offices).
*   **Intent Recognition:** Developed a basic logic to identify commands like "open", "run", "hello", and "stop".
*   **Silent Feedback System:** Implemented a terminal-based feedback loop. The assistant currently "responds" via text to ensure stability during the initial testing phase.

---

## 📅 Week 3: Core Assistant Mechanics & System Integration
This week marks a major milestone where the core architecture of the desktop assistant was established and primary commands for operating system interaction were implemented. 

> **Note:** To ensure a faster and error-free development cycle, all assistant responses are currently routed to **terminal (console) outputs**.

### 🚀 New Features
*   **Time & Date:** Implemented the `datetime` module to provide real-time local information.
*   **Social Interaction:** Added basic conversational capabilities such as greetings and small talk.
*   **Native Integration:** Utilized the `os` module to launch Windows applications like **Notepad**, **Calculator**, and **Spotify** without external dependencies.
*   **Web Navigation:** Implemented the `webbrowser` module to trigger the default browser for Google searches, YouTube, and custom media URLs.
*   **External API Integration (Weather Service):** Integrated the **OpenWeatherMap API** to provide real-time weather updates. 
*   **Graceful Exit:** Added secure termination triggers (e.g., "exit", "close", "stop") to stop the background infinite loop safely.

---

## 📅 Week 4 Update: Advanced Automation & NLP Engine Upgrade
This week focused on making the assistant more autonomous, enhancing the text-to-speech quality, and completely overhauling the command recognition logic for better scalability.

### 🚀 New Features
*   **Dynamic Intent Recognition:** Shifted the command recognition logic from static conditions to a dynamic, dictionary-based mapping system (`KOMUTLAR`).
*   **Continuous Listening & Wake Word:** Implemented a background standby mode, actively listening for triggers like "hey asistan" before engaging the main interaction engine.
*   **Voice Engine Overhaul:** Upgraded the text-to-speech implementation by transitioning to `gTTS` (Google Text-to-Speech) for a much higher-quality, natural-sounding Turkish voice.
*   **Advanced Desktop Automation:** Integrated `pyautogui` for hardware-level simulation to control system volume and capture automated screenshots.
*   **Live Information & RSS Feeds:** Added the ability to fetch, summarize, and dictate information via the **Wikipedia API** and parse real-time breaking news via **TRT Haber RSS**.

---

## 📅 Week 5 Update: Modern GUI, Async Processing & Fuzzy NLP (Latest Update)
This week, the project evolved from a terminal script into a standalone desktop application. The focus was on user interface, performance optimization, and making the assistant's understanding "smarter" using fuzzy logic.

### 🚀 New Features

#### 🖥️ Modern Graphical User Interface (GUI)
Integrated `customtkinter` to replace the terminal console. The application now features a sleek, dark-themed UI that displays real-time status updates ("Listening...", "Processing...") and a live scrollable chat log.

#### ⚡ Asynchronous Processing (Threading)
Implemented the `threading` module to separate the voice recognition engine from the GUI main loop. The assistant now actively listens and responds in the background without freezing the application interface.

#### 🧠 Fuzzy NLP Matching
Integrated the `thefuzz` library (Levenshtein distance) to intelligently interpret user commands and launch applications. The assistant no longer requires exact phrasing; it matches commands with a >70-75% accuracy threshold, gracefully handling mispronunciations or natural language variations.

#### 🚀 In-Memory TTS (Lightning Fast Audio)
Completely refactored the text-to-speech pipeline. Instead of saving temporary `.mp3` files to the hard drive, the assistant now writes the `gTTS` audio stream directly to an in-memory buffer (`io.BytesIO`) and plays it instantly using `pygame.mixer`. This resulted in zero-latency responses.

#### 📚 Optimized Knowledge Retrieval
Refactored the Wikipedia search logic (disabling auto-suggest and limiting results) to drastically reduce API response times and prevent unnecessary background requests.

### 🛠️ Technologies & Dependencies

| Category | Tools / Libraries |
| :--- | :--- |
| **GUI & Core** | `customtkinter`, `threading`, `sys`, `subprocess` |
| **Audio Processing** | `SpeechRecognition`, `gTTS`, `pygame`, `io` |
| **NLP & Logic** | `thefuzz` (fuzzy matching), `random`, `time` |
| **Automation** | `pyautogui`, `webbrowser`, `os` |
| **Data & APIs** | OpenWeatherMap API, `wikipedia`, `requests`, `feedparser` |

---

## ⚙️ How to Run

**1. Install dependencies:**
```bash
pip install SpeechRecognition gTTS pygame customtkinter thefuzz wikipedia pyautogui feedparser requests
