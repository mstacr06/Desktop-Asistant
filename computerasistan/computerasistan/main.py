import speech_recognition as sr
import datetime
import os
import random
import requests
import time
from gtts import gTTS
import io
import pygame
import wikipedia
import pyautogui
import feedparser
import threading
import customtkinter as ctk
from thefuzz import process
import sys
import subprocess
import webbrowser

# -----------------------------------
# AYARLAR
# -----------------------------------
API_KEY = "b8768819961d2139e8acbafc2ad8c1f2"
DEMO_MODE = False

# Ses motorunu başlat (Hızlı RAM oynatması için)
pygame.mixer.init()

listener = sr.Recognizer()
listener.pause_threshold = 1
listener.dynamic_energy_threshold = True
listener.energy_threshold = 300

# -----------------------------------
# KOMUTLAR
# -----------------------------------
KOMUTLAR = {
    "selamlasma": ["merhaba", "selam", "naber", "nasılsın", "ne haber", "napıyosun", "hey"],
    "saat": ["saat kaç", "saat", "zaman nedir"],
    "tarih": ["bugün tarih ne", "tarih", "ayın kaçı"],
    "saka": ["şaka yap", "beni güldür", "espri yap"],
    "hava": ["hava durumu", "hava nasıl", "kaç derece"],
    "bilgi": ["kimdir", "nedir", "hakkında bilgi", "araştır"],
    "haber": ["haberler", "gündem", "son dakika"],
    "yazi_tura": ["yazı tura", "para at"],
    "zar": ["zar at", "zar salla"],
    "ekran_goruntusu": ["ekran görüntüsü", "ss al"],
    "ses_kapat": ["sesi kapat", "sessize al"],
    "ses_ac": ["sesi aç"],
    "ses_yukselt": ["ses yükselt", "ses arttır"],
    "ses_kis": ["sesi kıs", "sesi azalt"],
    "uygulama_ac": ["aç", "başlat", "çalıştır", "açar mısın", "açsana", "başlatır mısın", "hadi aç", "açalım"],
    "cikis": ["kapat", "uyu", "görüşürüz", "baybay", "çıkış yap"]
}

# -----------------------------------
# GUI (ARAYÜZ) AYARLARI
# -----------------------------------
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.geometry("450x600")
app.title("Yapay Zeka Asistanı")

# UI Elemanları
status_label = ctk.CTkLabel(app, text="Sistem Başlatılıyor...", font=("Arial", 18, "bold"), text_color="#00FFA3")
status_label.pack(pady=20)

log_textbox = ctk.CTkTextbox(app, width=400, height=450, state="disabled", font=("Consolas", 14))
log_textbox.pack(pady=10)

def ui_log(text):
    """Safely updates the GUI textbox from the background thread."""
    def update():
        log_textbox.configure(state="normal")
        log_textbox.insert("end", text + "\n")
        log_textbox.see("end")
        log_textbox.configure(state="disabled")
    app.after(0, update)

def ui_status(text):
    """Safely updates the main status label."""
    app.after(0, lambda: status_label.configure(text=text))

# -----------------------------------
# SES MOTORU (HIZLANDIRILMIŞ)
# -----------------------------------
def speak(text):
    try:
        # Sesi Google'dan alıyoruz (lang='tr' ile doğrudan Türkçe)
        tts = gTTS(text=text, lang='tr', slow=False)
        
        # Sesi diske kaydetmek yerine RAM'de (bellekte) tutuyoruz
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0) # Dosyanın başına dön
        
        # Pygame ile sesi bellekten anında çalıyoruz
        pygame.mixer.music.load(fp, "mp3")
        pygame.mixer.music.play()
        
        # Ses bitene kadar bekle (Asistanın lafı bitmeden dinlemeye geçmemesi için)
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
    except Exception as e:
        ui_log(f"[SES HATASI]: {e}")

def asistan_mesaj(text):
    ui_log(f"🤖 Asistan: {text}")
    speak(text)

# -----------------------------------
# DİNLEME
# -----------------------------------
is_noise_adjusted = False

def take_command(mesaj="Dinleniyor...", timeout_suresi=8, limit_suresi=15):
    global is_noise_adjusted
    command = ""
    try:
        with sr.Microphone() as source:
            if not is_noise_adjusted:
                ui_status("Ortam Sesi Ayarlanıyor...")
                listener.adjust_for_ambient_noise(source, duration=1)
                is_noise_adjusted = True

            ui_status(mesaj)
            audio = listener.listen(source, timeout=timeout_suresi, phrase_time_limit=limit_suresi)
            
            ui_status("İşleniyor...")
            command = listener.recognize_google(audio, language="tr-TR").lower()
            ui_log(f"👤 Sen: {command}")

    except sr.WaitTimeoutError:
        pass
    except sr.UnknownValueError:
        pass
    except Exception as e:
        ui_log(f"[MİKROFON HATASI]: {e}")

    return command.strip()

# -----------------------------------
# WAKE WORD
# -----------------------------------
WAKE_WORDS = ["hey asistan", "asistan", "orda mısın"]

def listen_for_wake_word():
    ui_status("Uyandırma Kelimesi Bekleniyor")
    command = take_command(mesaj="...", timeout_suresi=5, limit_suresi=5)
    
    # Using basic matching for wake words to avoid false triggers
    return any(wake_word in command for wake_word in WAKE_WORDS)

# -----------------------------------
# INTENT BUL (FUZZY MATCHING)
# -----------------------------------
def intent_bul(command):
    """
    Uses Levenshtein distance to find the closest matching intent.
    Returns None if the confidence score is below 75.
    """
    best_intent = None
    highest_score = 0

    for niyet, kelimeler in KOMUTLAR.items():
        # extractOne compares the command to all keywords in the list and returns the highest match
        match, score = process.extractOne(command, kelimeler)
        
        if score > highest_score:
            highest_score = score
            best_intent = niyet

    # Threshold: Only accept if the match is at least 75% accurate
    if highest_score >= 75:
        return best_intent
        
    return None

# -----------------------------------
# YARDIMCI FONKSİYONLAR
# -----------------------------------
def tell_time():
    now = datetime.datetime.now()
    asistan_mesaj("Şu an saat " + now.strftime("%H:%M"))

def tell_date():
    now = datetime.datetime.now()
    asistan_mesaj("Bugünün tarihi " + now.strftime("%d.%m.%Y"))

def tell_joke():
    jokes = [
        "Yazılımcının sevgilisi neden ayrılmış? Çünkü adam her tartışmada sistemde bug var demiş.",
        "İki bit yolda karşılaşıyor. Biri diyor ki sıfırın altındayım kardeşim."
    ]
    asistan_mesaj(random.choice(jokes))

def get_city(command):
    # Modified slightly to handle fuzzy extraction gracefully
    temizlenecek_ekstra = ["da", "de", "için", "söyle", "hava", "durumu", "nasıl"]
    kelimeler = command.split()
    city_words = [k for k in kelimeler if k not in temizlenecek_ekstra]
    city = " ".join(city_words).strip()
    return city.title() if city else "Kayseri"

def weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=tr"
        response = requests.get(url)
        data = response.json()

        if data["cod"] != 200:
            asistan_mesaj("Şehri bulamadım.")
            return

        derece = data["main"]["temp"]
        durum = data["weather"][0]["description"]
        asistan_mesaj(f"{city} için hava {durum}. Sıcaklık {round(derece)} derece.")
    except:
        asistan_mesaj("Hava durumunu çekemedim.")

def search_wikipedia(command):
    temizlenecek = ["kimdir", "nedir", "hakkında", "bilgi", "araştır"]
    kelimeler = command.split()
    query_words = [k for k in kelimeler if k not in temizlenecek]
    query = " ".join(query_words).strip()

    if not query:
        asistan_mesaj("Neyi araştırmamı istersin?")
        return

    ui_status("Vikipedi'de aranıyor...") 
    
    try:
        wikipedia.set_lang("tr")
        
        # 1. ADIM: Doğrudan sayfa çekmek yerine önce en iyi 1 sonucu aratıyoruz (Daha isabetli)
        arama_sonuclari = wikipedia.search(query, results=1)
        
        if not arama_sonuclari:
            asistan_mesaj("Vikipedi'de bununla ilgili bir şey bulamadım.")
            return
            
        en_iyi_sonuc = arama_sonuclari[0]
        
        # 2. ADIM: auto_suggest=False yaparak gereksiz 2. API isteğini engelliyoruz (Hızlandırır)
        sonuc = wikipedia.summary(en_iyi_sonuc, sentences=2, auto_suggest=False)
        asistan_mesaj(sonuc)
        
    except wikipedia.exceptions.DisambiguationError as e:
        # HATA YÖNETİMİ: Eğer aranan kelime birden fazla anlama geliyorsa
        try:
            ilk_secenek = e.options[0]
            sonuc = wikipedia.summary(ilk_secenek, sentences=2, auto_suggest=False)
            asistan_mesaj(sonuc)
        except:
            asistan_mesaj("Bununla ilgili birden fazla sonuç var, biraz daha spesifik söyler misin?")
            
    except wikipedia.exceptions.PageError:
        asistan_mesaj("Vikipedi'de böyle bir sayfa bulamadım.")
    except Exception as e:
        ui_log(f"[WIKI HATASI]: {e}")
        asistan_mesaj("Araştırma sırasında bir hata oluştu.")

# -----------------------------------
# UYGULAMA AÇMA (FUZZY MATCHING İLE)
# -----------------------------------
def open_application(command):
    uygulamalar = {
        "spotify": "spotify",
        "google chrome": "chrome",
        "chrome": "chrome",
        "not defteri": "notepad",
        "hesap makinesi": "calc",
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "word": "winword",
        "excel": "excel",
        "powerpoint": "powerpnt",
        "paint": "mspaint",
        "görev yöneticisi": "taskmgr",
        "komut istemi": "cmd",
        "denetim masası": "control",
        "ayarlar": "ms-settings:",
        "dosya gezgini": "explorer",
        "steam": "steam",
        "discord": "discord",
        "whatsapp": "whatsapp",
        "twitter": "https://www.twitter.com",
        "instagram": "https://www.instagram.com",
        "github": "https://www.github.com",
        "chatgpt": "https://chatgpt.com"
    }

    # Cümle içinde uygulama adını fuzzy matching ile arıyoruz
    en_iyi_eslesme, skor = process.extractOne(command, list(uygulamalar.keys()))

    if skor >= 70:  # Eğer eşleşme oranı %70 ve üzeriyse
        asistan_mesaj(f"{en_iyi_eslesme.title()} açılıyor...")
        hedef = uygulamalar[en_iyi_eslesme]
        try:
            if hedef.startswith("http"):
                webbrowser.open(hedef)
            elif sys.platform == 'win32':
                os.system(f"start {hedef}")
            elif sys.platform == 'darwin':
                subprocess.call(['open', '-a', hedef])
            else:
                subprocess.call([hedef])
        except Exception as e:
            ui_log(f"[UYGULAMA AÇMA HATASI]: {e}")
            asistan_mesaj("Uygulamayı açarken bir sorun oluştu.")
    else:
        asistan_mesaj("Hangi uygulamayı açmamı istediğini tam anlayamadım.")

# -----------------------------------
# ANA ASİSTAN DÖNGÜSÜ
# -----------------------------------
def run_assistant():
    while True:
        command = take_command(mesaj="Seni dinliyorum...", timeout_suresi=8, limit_suresi=15)

        if len(command) < 2:
            continue

        niyet = intent_bul(command)

        if niyet == "selamlasma":
            cevaplar = ["Merhaba kral.", "Buradayım kral.", "Seni dinliyorum."]
            asistan_mesaj(random.choice(cevaplar))
        elif niyet == "saat":
            tell_time()
        elif niyet == "tarih":
            tell_date()
        elif niyet == "saka":
            tell_joke()
        elif niyet == "hava":
            city = get_city(command)
            weather(city)
        elif niyet == "bilgi":
            search_wikipedia(command)
        elif niyet == "haber":
            asistan_mesaj("Haberler çekiliyor...")
        elif niyet == "yazi_tura":
            asistan_mesaj(f"Sonuç: {random.choice(['Yazı', 'Tura'])}")
        elif niyet == "zar":
            asistan_mesaj(f"Gelen sayı: {random.randint(1, 6)}")
        elif niyet == "ekran_goruntusu":
            if not DEMO_MODE:
                pyautogui.screenshot(f"ekran_{int(time.time())}.png")
            asistan_mesaj("Ekran görüntüsü alındı.")
        elif niyet == "uygulama_ac":
            open_application(command)
        elif niyet in ["ses_kapat", "ses_ac", "ses_yukselt", "ses_kis"]:
            asistan_mesaj(f"{niyet.replace('_', ' ')} işlemi yapıldı.")
        elif niyet == "cikis":
            asistan_mesaj("Tamam kral. Tekrar çağırırsan buradayım.")
            return True
        else:
            asistan_mesaj("Bunu tam anlayamadım. Farklı şekilde söyler misin?")

# -----------------------------------
# THREAD BAŞLATMA
# -----------------------------------
def background_listener():
    time.sleep(1) # Let GUI load
    ui_log("Sistem hazır. Uyandırılmayı bekliyorum.")
    
    while True:
        if listen_for_wake_word():
            asistan_mesaj(random.choice(["Efendim?", "Dinliyorum.", "Buradayım."]))
            run_assistant()

# Ayrı bir thread üzerinde dinleme motorunu başlatıyoruz
threading.Thread(target=background_listener, daemon=True).start()

# GUI Ana Döngüsünü başlat
app.mainloop()