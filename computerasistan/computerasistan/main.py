# GEREKLİ KURULUM:
# pip install SpeechRecognition requests pyaudio

import speech_recognition as sr
import datetime
import webbrowser
import os
import random
import requests
import time

# -----------------------------------
# AYARLAR
# -----------------------------------

API_KEY = "b8768819961d2139e8acbafc2ad8c1f2"

listener = sr.Recognizer()

# -----------------------------------
# TERMİNALE YAZDIRMA 
# -----------------------------------

def asistan_mesaj(text):
    """Asistanın yanıtlarını sadece terminale yazdırır."""
    print(f"\nAsistan: {text}")

# -----------------------------------
# KOMUT DİNLEME
# -----------------------------------

def take_command():
    command = ""

    try:
        with sr.Microphone() as source:
            print("\nDinleniyor...")
            listener.adjust_for_ambient_noise(source, duration=1)
            audio = listener.listen(source)

            command = listener.recognize_google(
                audio,
                language="tr-TR"
            )

            command = command.lower()
            print(f"Sen: {command}")

    except:
        pass

    return command

# -----------------------------------
# SAAT
# -----------------------------------

def tell_time():
    now = datetime.datetime.now()
    saat = now.strftime("%H:%M")
    asistan_mesaj("Şu an saat " + saat)

# -----------------------------------
# TARİH
# -----------------------------------

def tell_date():
    now = datetime.datetime.now()
    tarih = now.strftime("%d.%m.%Y")
    asistan_mesaj("Bugünün tarihi " + tarih)

# -----------------------------------
# ŞAKA
# -----------------------------------

def tell_joke():
    jokes = [
        "Yazılımcının sevgilisi neden ayrılmış? Çünkü adam her tartışmada 'sorun sende değil, sistemde bug var' demiş."
    ]
    asistan_mesaj(random.choice(jokes))

# -----------------------------------
# ŞEHİR ALGILAMA
# -----------------------------------

def get_city(command):
    temizlenecek = [
        "hava", "durumu", "nasıl", "kaç",
        "derece", "bugün", "yarın",
        "söyle", "bana", "nedir"
    ]

    kelimeler = command.split()
    city_words = []

    for kelime in kelimeler:
        if kelime not in temizlenecek:
            city_words.append(kelime)

    city = " ".join(city_words).strip()

    if city == "":
        city = "Istanbul"

    return city.title()

# -----------------------------------
# HAVA DURUMU
# -----------------------------------

def weather(city):
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={city}&appid={API_KEY}&units=metric&lang=tr"
        )

        response = requests.get(url)
        data = response.json()

        if data["cod"] != 200:
            asistan_mesaj("Şehir bulunamadı.")
            return

        derece = data["main"]["temp"]
        hissedilen = data["main"]["feels_like"]
        durum = data["weather"][0]["description"]

        mesaj = (
            f"{city} için güncel hava durumu: {durum}. "
            f"Sıcaklık {round(derece)} derece, hissedilen {round(hissedilen)} derece."
        )

        asistan_mesaj(mesaj)

    except:
        asistan_mesaj("Hava durumu bilgisi alınamadı.")

# -----------------------------------
# KOMUTLAR
# -----------------------------------

def run_assistant():
    command = take_command()
    time.sleep(0.3)

    if "merhaba" in command or "selam" in command or "hello" in command or "hi" in command:
        asistan_mesaj("Merhaba kral. Emrindeyim.")

    elif "nasılsın" in command or "ne yapıyorsun" in command or "naber" in command or "ne haber" in command:
        asistan_mesaj("Gayet iyiyim kral.")

    elif "saat kaç" in command or "saati söyle" in command:
        tell_time()

    elif "bugün tarih ne" in command or "tarih söyle" in command:
        tell_date()

    elif "youtube aç" in command:
        asistan_mesaj("YouTube açılıyor.")
        webbrowser.open("https://www.youtube.com")

    elif "google aç" in command:
        asistan_mesaj("Google açılıyor.")
        webbrowser.open("https://www.google.com")

    elif "müzik aç" in command:
        asistan_mesaj("Müzik açılıyor.")
        webbrowser.open("https://www.youtube.com/results?search_query=music")

    elif "favori müzik aç" in command:
        asistan_mesaj("Favori müzik açılıyor.")
        webbrowser.open("https://www.youtube.com/watch?v=6mMGQ4fci7U")

    elif "hesap makinesi aç" in command:
        asistan_mesaj("Hesap makinesi açılıyor.")
        os.system("calc")

    elif "not defteri aç" in command:
        asistan_mesaj("Not defteri açılıyor.")
        os.system("notepad")

    elif "şaka yap" in command:
        tell_joke()

    elif "spotify" in command:
        asistan_mesaj("Spotify açılıyor.")
        os.system("spotify")    

    elif "hava durumu" in command:
        city = get_city(command)
        weather(city)

    elif "kapat" in command or "çıkış yap" in command or "çık" in command or "görüşürüz" in command:
        asistan_mesaj("Görüşürüz kral.")
        exit()

    elif command != "":
        asistan_mesaj("Bunu anlayamadım, tekrar söyler misin?")

# -----------------------------------
# BAŞLANGIÇ
# -----------------------------------

print("-----------------------------------------")
asistan_mesaj("Merhaba. Yapay zekan hazır.")
print("-----------------------------------------")

while True:
    run_assistant()