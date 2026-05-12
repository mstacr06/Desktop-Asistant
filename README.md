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

   
Week 3: Core Assistant Mechanics & System Integration

During this week, the foundational structure of the desktop assistant was implemented and core system interaction features were developed.
For faster debugging and a more stable development workflow, all assistant responses were temporarily directed to the terminal/console output.

🚀 Features Implemented
🎤 Speech-to-Text Recognition

Integrated the SpeechRecognition library to capture voice commands from the microphone and convert them into text.

🖥️ System Commands
Retrieved and displayed the local system date and time using the datetime module.
Added basic conversational responses such as greetings and simple interactions.
⚙️ Application & Browser Automation
Used os.system to launch built-in Windows applications such as:
Notepad
Calculator
Spotify
Used the webbrowser module to open:
Google
YouTube
Predefined media links
🌦️ Weather API Integration

Integrated the OpenWeatherMap API to provide real-time weather information.
The assistant extracts the city name from the spoken command and sends HTTP requests using the requests module.

❌ Graceful Exit System

Implemented controlled shutdown commands such as:

"exit"
"close"
"shutdown assistant"

This allows the assistant loop to terminate safely without forcing the program to stop manually.

🛠️ Technologies & Libraries Used
External Libraries
SpeechRecognition
PyAudio
requests
Standard Python Libraries
os
datetime
webbrowser
random
time
