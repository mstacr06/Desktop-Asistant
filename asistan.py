import speech_recognition as sr
import pyttsx3
import sys


engine = pyttsx3.init()
engine.setProperty('rate', 170) 

def speak(text):
    """Asistanın sesli geri bildirim yapmasını ENGELLEDİK, sadece yazdırır"""
    print(f"\n[Assistant]: {text}")
   

def listen_for_command():
    """Mikrofonu dinler ve sesi metne çevirir"""
    recognizer = sr.Recognizer()

    print("\n--- [SYSTEM]: I am listening to you... (Say something) ---")

    with sr.Microphone() as source:
        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            return None

    try:
        command = recognizer.recognize_google(audio, language="en-US").lower()
        print(f"[User Said]: {command}")
        return command
    except sr.UnknownValueError:
        print("[System]: Sound detected but could not be understood.")
        return None
    except sr.RequestError:
        print("[System]: Connection error.")
        return None

def main():
    print("========================================")
    print("    VOICE RECOGNITION DEMO MODE ONLY")
   
    print("========================================")
    
    print("\n[System]: Demo mode is active. Ready to listen.")

    while True:
        command = listen_for_command()

        if command is None:
            continue

        if "exit" in command or "stop" in command or "close" in command:
            speak("Exiting demo mode. Goodbye!")
            break

        if "open" in command or "run" in command or "start" in command :
            app_name = command.replace("open", "").strip()
            speak(f"I understood that you want to open {app_name}, but I am in demo mode.")
        
        elif "hello" in command or "hi" in command:
            speak("Hello there! I can hear you clearly.")
            
        else:
            speak(f"You said: {command}. I processed this intent correctly.")

if __name__ == "__main__":
    main()