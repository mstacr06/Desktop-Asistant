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
import threading
import customtkinter as ctk
from thefuzz import process
import sys
import subprocess
import webbrowser
import feedparser 

# Wikipedia API'sine kendimizi tanıtıyoruz ki bizi engellemesin
wikipedia.set_user_agent("AsistanProjesi/1.0 (wmustafaacarw@gmail.com)")

# -----------------------------------
# AYARLAR
# -----------------------------------
API_KEY = "b8768819961d2139e8acbafc2ad8c1f2"
DEMO_MODE = False

# Ses motorunu başlat
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
    "uygulama_ac": [
        "aç", "başlat", "çalıştır", "açar mısın", 
        "whatsapp aç", "spotify aç", "youtube aç", "chrome aç", 
        "uygulama aç", "program aç"
    ],
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
# SES MOTORU (HIZLANDIRILMIŞ VE HATASIZ)
# -----------------------------------
def speak(text):
    try:
        tts = gTTS(text=text, lang='tr', slow=False)
        
        # Temp hatasını çözmek için her sese özel (zaman damgalı) isim veriyoruz
        temp_file = f"temp_voice_{int(time.time() * 1000)}.mp3"
        tts.save(temp_file)
        
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        # Şarkı/ses bitince dosyayı bellekten sal ve bilgisayardan sil
        pygame.mixer.music.unload()
        try:
            os.remove(temp_file)
        except:
            pass
            
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
    return any(wake_word in command for wake_word in WAKE_WORDS)

# -----------------------------------
# INTENT BUL (AKILLI FUZZY MATCHING)
# -----------------------------------
def intent_bul(command):
    # Ses karışıklığını önle: Cümlede "ses" yoksa ses komutlarını arama
    if "ses" not in command:
        aranacak_komutlar = {k: v for k, v in KOMUTLAR.items() if not k.startswith("ses_")}
    else:
        aranacak_komutlar = KOMUTLAR

    best_intent = None
    highest_score = 0

    for niyet, kelimeler in aranacak_komutlar.items():
        match, score = process.extractOne(command, kelimeler)
        
        if score > highest_score:
            highest_score = score
            best_intent = niyet

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
    temizlenecek_ekstra = ["da", "de", "için", "söyle", "hava", "durumu", "nasıl"]
    kelimeler = command.split()
    city_words = [k for k in kelimeler if k not in temizlenecek_ekstra]
    city = " ".join(city_words).strip()
    return city.title() if city else "Kayseri"

def weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=tr"
        response = requests.get(url)
        
        if response.status_code != 200:
            ui_log(f"[HAVA API HATASI]: Kod {response.status_code}")
            asistan_mesaj("Hava durumu servisine şu an erişemiyorum.")
            return

        data = response.json()
        derece = data["main"]["temp"]
        durum = data["weather"][0]["description"]
        asistan_mesaj(f"{city} için hava {durum}. Sıcaklık {round(derece)} derece.")
    except Exception as e:
        ui_log(f"[HAVA DURUMU HATASI]: {e}")
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
        sonuc = wikipedia.summary(query, sentences=2, auto_suggest=True)
        asistan_mesaj(sonuc)
        
    except wikipedia.exceptions.DisambiguationError as e:
        if e.options:
            try:
                ilk_secenek = e.options[0]
                sonuc = wikipedia.summary(ilk_secenek, sentences=2, auto_suggest=False)
                asistan_mesaj(sonuc)
            except:
                asistan_mesaj("Bununla ilgili çok fazla sonuç var, biraz daha spesifik söyler misin?")
        else:
            asistan_mesaj("Tam olarak neyi kastettiğini anlayamadım.")
            
    except wikipedia.exceptions.PageError:
        asistan_mesaj("Vikipedi'de böyle bir sayfa bulamadım.")
    except Exception as e:
        ui_log(f"[WIKI HATASI]: {e}")
        asistan_mesaj("Araştırma sırasında bir hata oluştu.")

# -----------------------------------
# UYGULAMA AÇMA (SINIRSIZ - DİNAMİK ARAMA)
# -----------------------------------
def open_application(command):
    temizlenecek = ["aç", "başlat", "çalıştır", "açar", "mısın", "lütfen"]
    kelimeler = command.split()
    uygulama_adi = " ".join([k for k in kelimeler if k not in temizlenecek]).strip()

    if not uygulama_adi:
        asistan_mesaj("Neyi açmamı istersin?")
        return

    asistan_mesaj(f"{uygulama_adi.title()} açılıyor...")
    
    # Çok sık kullanılan web siteleri ve özel uygulamalar
    ozel_siteler = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "chatgpt": "https://chatgpt.com",
        "whatsapp": "whatsapp://"
    }
    
    if uygulama_adi in ozel_siteler:
        try:
            if uygulama_adi == "whatsapp":
                os.system(f"start {ozel_siteler[uygulama_adi]}")
            else:
                webbrowser.open(ozel_siteler[uygulama_adi])
        except:
            pass
        return

    # Eğer web sitesi veya özel kısayol değilse bilgisayarda dinamik arama yap
    try:
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write(uygulama_adi, interval=0.05)
        time.sleep(0.5)
        pyautogui.press("enter")
    except Exception as e:
        ui_log(f"[UYGULAMA AÇMA HATASI]: {e}")
        asistan_mesaj("Uygulamayı açarken bir sorun oluştu.")

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
            get_news()
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
            
        # GERÇEK SES KONTROLLERİ
        elif niyet == "ses_kapat":
            pyautogui.press("volumemute") 
            asistan_mesaj("Ses kapatıldı.")
        elif niyet == "ses_ac":
            # Barın kalması veya çalışmaması bug'ını önlemek için Sesi Aç tuşu tetiklenir
            for _ in range(2): pyautogui.press("volumeup")
            asistan_mesaj("Ses açıldı.")
        elif niyet == "ses_yukselt":
            for _ in range(5): pyautogui.press("volumeup") 
            asistan_mesaj("Ses yükseltildi.")
        elif niyet == "ses_kis":
            for _ in range(5): pyautogui.press("volumedown")
            asistan_mesaj("Ses kısıldı.")
            
        elif niyet == "cikis":
            asistan_mesaj("Tamam kral. Tekrar çağırırsan buradayım.")
            return True
        else:
            asistan_mesaj("Bunu tam anlayamadım. Farklı şekilde söyler misin?")

            #haber çekme
def get_news():
    try:
        # Google Haberler (Türkiye) güncel RSS kaynağı
        url = "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"
        feed = feedparser.parse(url)
        
        if not feed.entries:
            asistan_mesaj("Şu an haber kaynağına ulaşamıyorum.")
            return

        asistan_mesaj("İşte Türkiye'den ve dünyadan güncel 3 haber başlığı:")
        
        # En güncel ilk 3 haberi çekip okutuyoruz
        for i, entry in enumerate(feed.entries[:3]):
            # Google haber başlıklarının sonundaki kaynak kısmını (örn: " - NTV") temizleyelim ki güzel okusun
            baslik = entry.title.split(" - ")[0]
            asistan_mesaj(f"{i+1}. haber: {baslik}")
            time.sleep(0.5) # Haberler arasına çok kısa bir es koy
            
    except Exception as e:
        ui_log(f"[HABER HATASI]: {e}")
        asistan_mesaj("Haberleri çekerken bir sorun oluştu.")
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