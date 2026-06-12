import speech_recognition as sr
import datetime
import os
import random
import requests
import time
from gtts import gTTS
import pygame
import wikipedia
import pyautogui
import threading
import customtkinter as ctk
import sys
import subprocess
import webbrowser
import feedparser
import math
import re
from deep_translator import GoogleTranslator

# Wikipedia API tanıtımı
wikipedia.set_user_agent("AsistanProjesi/1.0 (wmustafaacarw@gmail.com)")

# -----------------------------------
# AYARLAR
# -----------------------------------
API_KEY = "b8768819961d2139e8acbafc2ad8c1f2"
DEMO_MODE = False

pygame.mixer.init()

listener = sr.Recognizer()
listener.pause_threshold = 1

listener.dynamic_energy_threshold = True
listener.energy_threshold = 300

# -----------------------------------
# INTENT MOTORU — Kural Tabanlı + Fuzzy Hibrit
# -----------------------------------
#
# Her intent için iki katman tanımlanır:
#   "zorunlu"  : Bu anahtar kelimelerden EN AZ BİRİ cümlede geçmeli.
#                Geçmiyorsa bu intent hiç değerlendirilmez. (False positive önler)
#   "destek"   : Fuzzy skorlamada kullanılacak örnek ifadeler.
#                Zorunlu koşul sağlandıktan sonra en yüksek skor kazanır.
#
# Sıralama önemlidir: daha spesifik intent'ler üstte olmalı.
# -----------------------------------

INTENT_KURALLARI = {

    # --- ÇEVİRİ (önce kontrol et: "ne demek" bilgiden önce gelmeli) ---
    "ceviri": {
        "zorunlu": ["çevir", "ne demek", "ingilizce", "türkçe", "translate"],
        "destek":  ["çevir", "ingilizceye çevir", "türkçeye çevir", "ne demek", "translate et"],
    },

    # --- MATEMATİK (sayı + operatör veya "hesapla" zorunlu) ---
    "matematik": {
        "zorunlu": ["hesapla", "kaç eder", "artı", "eksi", "çarpı", "bölü", "topla", "çarp", "böl"],
        "destek":  ["hesapla", "kaç eder", "topla", "çarp", "böl", "artı", "eksi", "çarpı", "bölü"],
    },

    # --- SES KOMUTLARI (hepsi "ses" veya "volume" zorunlu) ---
    "ses_kapat": {
        "zorunlu": ["ses"],
        "destek":  ["sesi kapat", "sessize al", "ses kapat", "sesi kes"],
        "ekstra_zorunlu": ["kapat", "kes", "sessize"],   # ses + bunlardan biri
    },
    "ses_ac": {
        "zorunlu": ["ses"],
        "destek":  ["sesi aç", "ses aç"],
        "ekstra_zorunlu": ["aç"],
    },
    "ses_yukselt": {
        "zorunlu": ["ses"],
        "destek":  ["ses yükselt", "sesi artır", "ses arttır", "sesi yükselt"],
        "ekstra_zorunlu": ["yükselt", "artır", "arttır"],
    },
    "ses_kis": {
        "zorunlu": ["ses"],
        "destek":  ["sesi kıs", "sesi azalt", "ses kıs", "ses azalt"],
        "ekstra_zorunlu": ["kıs", "azalt"],
    },

    # --- UYGULAMA AÇ ---
    # "aç" tek başına yeterli DEĞİL — yanında bir uygulama adı olmalı.
    # Bunu open_application() içinde hallederiz; burada sadece "aç/başlat" zorunlu.
    "uygulama_ac": {
        "zorunlu": ["aç", "başlat", "çalıştır"],
        "destek":  ["youtube aç", "spotify aç", "chrome aç", "whatsapp aç",
                    "uygulama aç", "program aç", "başlat", "çalıştır"],
        # Ses komutlarıyla çakışmaması için "ses" içeren komutları dışla
        "yasak": ["ses"],
    },

    # --- ÇIKIŞ ---
    "cikis": {
        "zorunlu": ["kapat", "uyu", "görüşürüz", "baybay", "çıkış"],
        "destek":  ["kapat", "uyu", "görüşürüz", "baybay", "çıkış yap"],
        "yasak":   ["ses", "uygulama", "ekran"],
    },

    # --- HAVA DURUMU ---
    "hava": {
        "zorunlu": ["hava", "derece", "sıcaklık"],
        "destek":  ["hava durumu", "hava nasıl", "kaç derece", "sıcaklık"],
    },

    # --- HABER ---
    "haber": {
        "zorunlu": ["haber", "gündem", "son dakika"],
        "destek":  ["haberler", "gündem", "son dakika", "haber"],
    },

    # --- BİLGİ / WİKİPEDİ ---
    "bilgi": {
        "zorunlu": ["kimdir", "nedir", "hakkında", "araştır"],
        "destek":  ["kimdir", "nedir", "hakkında bilgi", "araştır"],
        "yasak":   ["ne demek"],   # çeviri ile çakışmasın
    },

    # --- SAAT ---
    "saat": {
        "zorunlu": ["saat", "zaman"],
        "destek":  ["saat kaç", "saat nedir", "zaman nedir"],
        "yasak":   ["hava"],
    },

    # --- TARİH ---
    "tarih": {
        "zorunlu": ["tarih", "ayın kaçı", "bugün"],
        "destek":  ["tarih nedir", "bugün tarih", "ayın kaçı"],
    },

    # --- ŞAKA ---
    "saka": {
        "zorunlu": ["şaka", "güldür", "espri"],
        "destek":  ["şaka yap", "beni güldür", "espri yap"],
    },

    # --- YAZI TURA ---
    "yazi_tura": {
        "zorunlu": ["yazı tura", "para at"],
        "destek":  ["yazı tura", "para at"],
    },

    # --- ZAR ---
    "zar": {
        "zorunlu": ["zar"],
        "destek":  ["zar at", "zar salla"],
    },

    # --- EKRAN GÖRÜNTÜSÜ ---
    "ekran_goruntusu": {
        "zorunlu": ["ekran", "ss al"],
        "destek":  ["ekran görüntüsü al", "ss al"],
    },

    # --- SELAMLAMA (en son: en geniş eşleşme) ---
    "selamlasma": {
        "zorunlu": ["merhaba", "selam", "naber", "nasılsın", "hey"],
        "destek":  ["merhaba", "selam", "naber", "nasılsın", "ne haber", "hey"],
    },
}


def intent_bul(command: str) -> str | None:
    """
    Hibrit intent sınıflandırıcı:
    1. Yasak kelime varsa → bu intent'i atla
    2. Zorunlu kelime yoksa → bu intent'i atla
    3. ekstra_zorunlu tanımlanmışsa → "zorunlu[0] VE ekstra_zorunlu'dan biri" koşulu ara
    4. Kalan adaylar arasında fuzzy skor hesapla → en yüksek skor ≥ 70 ise döndür
    """
    from thefuzz import process as fuzz_process

    adaylar = []

    for niyet, kural in INTENT_KURALLARI.items():
        zorunlular   = kural.get("zorunlu", [])
        yasaklar     = kural.get("yasak", [])
        ekstra_zor   = kural.get("ekstra_zorunlu", [])
        destek       = kural.get("destek", [])

        # 1. Yasak kelime kontrolü
        if any(yasak in command for yasak in yasaklar):
            continue

        # 2. Zorunlu kelime kontrolü
        zorunlu_gecti = any(z in command for z in zorunlular)
        if not zorunlu_gecti:
            continue

        # 3. ekstra_zorunlu varsa, ondan da en az biri geçmeli
        if ekstra_zor and not any(e in command for e in ekstra_zor):
            continue

        # 4. Aday listeye ekle + fuzzy skor
        _, skor = fuzz_process.extractOne(command, destek)
        adaylar.append((niyet, skor))

    if not adaylar:
        return None

    # En yüksek skorlu adayı seç
    en_iyi = max(adaylar, key=lambda x: x[1])

    # Minimum güven eşiği: 70
    if en_iyi[1] >= 70:
        ui_log(f"   🎯 Intent: {en_iyi[0]} (skor: {en_iyi[1]})", "sistem")
        return en_iyi[0]

    return None

# -----------------------------------
# GUI TASARIMI — Geliştirilmiş
# -----------------------------------
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.geometry("480x680")
app.title("AI Asistan")
app.resizable(False, False)

# Renk paleti
RENKLER = {
    "bg": "#0D0D0D",
    "panel": "#111827",
    "accent": "#00FFA3",
    "accent2": "#00BFFF",
    "text": "#E5E7EB",
    "muted": "#6B7280",
    "mic_idle": "#1F2937",
    "mic_active": "#00FFA3",
}

app.configure(fg_color=RENKLER["bg"])

# --- Başlık ---
header_frame = ctk.CTkFrame(app, fg_color=RENKLER["panel"], corner_radius=16)
header_frame.pack(fill="x", padx=20, pady=(18, 0))

title_label = ctk.CTkLabel(
    header_frame,
    text="⚡  AI Asistan",
    font=("SF Pro Display", 22, "bold"),
    text_color=RENKLER["accent"]
)
title_label.pack(side="left", padx=18, pady=12)

status_label = ctk.CTkLabel(
    header_frame,
    text="Başlatılıyor...",
    font=("SF Pro Display", 12),
    text_color=RENKLER["muted"]
)
status_label.pack(side="right", padx=18, pady=12)

# --- Mikrofon Animasyon Alanı ---
mic_frame = ctk.CTkFrame(app, fg_color=RENKLER["bg"], corner_radius=0)
mic_frame.pack(pady=(14, 0))

MIC_CANVAS_SIZE = 100
mic_canvas = ctk.CTkCanvas(
    mic_frame,
    width=MIC_CANVAS_SIZE,
    height=MIC_CANVAS_SIZE,
    bg=RENKLER["bg"],
    highlightthickness=0
)
mic_canvas.pack()

# Mikrofon ikonunu çiz
def draw_mic(active=False, pulse_r=0):
    mic_canvas.delete("all")
    cx, cy = MIC_CANVAS_SIZE // 2, MIC_CANVAS_SIZE // 2
    color = RENKLER["mic_active"] if active else RENKLER["mic_idle"]

    # Dış halkalar (animasyon)
    if active and pulse_r > 0:
        for i in range(3):
            alpha_color = ["#00FFA320", "#00FFA315", "#00FFA308"][i]
            r = pulse_r + i * 10
            mic_canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                   outline=RENKLER["accent"], width=1 + (2 - i) * 0.5)

    # Ana daire arka plan
    base_r = 36
    mic_canvas.create_oval(cx - base_r, cy - base_r, cx + base_r, cy + base_r,
                            fill=color, outline="")

    # Mikrofon gövdesi
    mic_canvas.create_rectangle(cx - 9, cy - 18, cx + 9, cy + 6,
                                 fill=RENKLER["bg"], outline="", width=0)
    # Mikrofon yarım daire üst
    mic_canvas.create_arc(cx - 9, cy - 20, cx + 9, cy - 4,
                          start=0, extent=180, fill=RENKLER["bg"], outline="")
    # Alt çizgi (sap)
    mic_canvas.create_line(cx, cy + 10, cx, cy + 18, fill=RENKLER["bg"], width=2)
    mic_canvas.create_line(cx - 7, cy + 18, cx + 7, cy + 18, fill=RENKLER["bg"], width=2)

# Animasyon state
mic_anim_running = False
mic_anim_angle = 0

def start_mic_animation():
    global mic_anim_running, mic_anim_angle
    mic_anim_running = True
    mic_anim_angle = 0
    animate_mic()

def stop_mic_animation():
    global mic_anim_running
    mic_anim_running = False
    app.after(0, lambda: draw_mic(active=False, pulse_r=0))

def animate_mic():
    global mic_anim_angle
    if not mic_anim_running:
        return
    mic_anim_angle = (mic_anim_angle + 4) % 360
    pulse = 20 + int(14 * abs(math.sin(math.radians(mic_anim_angle))))
    draw_mic(active=True, pulse_r=pulse)
    app.after(35, animate_mic)

draw_mic(active=False, pulse_r=0)

# --- Log kutusu ---
log_frame = ctk.CTkFrame(app, fg_color=RENKLER["panel"], corner_radius=16)
log_frame.pack(fill="both", expand=True, padx=20, pady=14)

log_textbox = ctk.CTkTextbox(
    log_frame,
    width=420,
    height=390,
    state="disabled",
    font=("Consolas", 13),
    fg_color=RENKLER["panel"],
    text_color=RENKLER["text"],
    scrollbar_button_color=RENKLER["accent"],
    corner_radius=12
)
log_textbox.pack(padx=10, pady=10, fill="both", expand=True)

# Tag renkleri
log_textbox._textbox.tag_configure("asistan", foreground=RENKLER["accent"])
log_textbox._textbox.tag_configure("kullanici", foreground=RENKLER["accent2"])
log_textbox._textbox.tag_configure("sistem", foreground=RENKLER["muted"])

# --- Alt durum şeridi ---
footer = ctk.CTkFrame(app, fg_color=RENKLER["panel"], corner_radius=10, height=36)
footer.pack(fill="x", padx=20, pady=(0, 14))
footer.pack_propagate(False)

footer_label = ctk.CTkLabel(
    footer,
    text="Uyandırma kelimesi: \"Asistan\" veya \"Hey Asistan\"",
    font=("Consolas", 11),
    text_color=RENKLER["muted"]
)
footer_label.pack(expand=True)

# -----------------------------------
# UI YARDIMCI FONKSİYONLARI
# -----------------------------------
def ui_log(text, tag="sistem"):
    def update():
        log_textbox.configure(state="normal")
        if text.startswith("🤖"):
            log_textbox._textbox.insert("end", text + "\n", "asistan")
        elif text.startswith("👤"):
            log_textbox._textbox.insert("end", text + "\n", "kullanici")
        else:
            log_textbox._textbox.insert("end", text + "\n", "sistem")
        log_textbox.see("end")
        log_textbox.configure(state="disabled")
    app.after(0, update)

def ui_status(text):
    app.after(0, lambda: status_label.configure(text=text))

# -----------------------------------
# SES MOTORU
# -----------------------------------
def speak(text):
    try:
        tts = gTTS(text=text, lang='tr', slow=False)
        temp_file = f"temp_voice_{int(time.time() * 1000)}.mp3"
        tts.save(temp_file)
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
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
            start_mic_animation()
            audio = listener.listen(source, timeout=timeout_suresi, phrase_time_limit=limit_suresi)
            stop_mic_animation()
            ui_status("İşleniyor...")
            command = listener.recognize_google(audio, language="tr-TR").lower()
            ui_log(f"👤 Sen: {command}")
    except sr.WaitTimeoutError:
        stop_mic_animation()
    except sr.UnknownValueError:
        stop_mic_animation()
    except Exception as e:
        stop_mic_animation()
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
        "İki bit yolda karşılaşıyor. Biri diyor ki sıfırın altındayım kardeşim.",
        "Neden programcılar karanlıktan korkmaz? Çünkü dark mode her zaman yanlarında.",
        "Bir yazılımcı eşine der ki: Markete git, bir ekmek al. Elma varsa on tane al. Eşi on ekmekle döner.",
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
                sonuc = wikipedia.summary(e.options[0], sentences=2, auto_suggest=False)
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

def get_news():
    try:
        url = "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"
        feed = feedparser.parse(url)
        if not feed.entries:
            asistan_mesaj("Şu an haber kaynağına ulaşamıyorum.")
            return
        asistan_mesaj("İşte güncel 3 haber başlığı:")
        for i, entry in enumerate(feed.entries[:3]):
            baslik = entry.title.split(" - ")[0]
            asistan_mesaj(f"{i + 1}. haber: {baslik}")
            time.sleep(0.5)
    except Exception as e:
        ui_log(f"[HABER HATASI]: {e}")
        asistan_mesaj("Haberleri çekerken bir sorun oluştu.")

def open_application(command):
    temizlenecek = {"aç", "başlat", "çalıştır", "açar", "mısın", "lütfen",
                    "bana", "benim", "için", "şunu", "şu"}
    kelimeler = command.split()
    uygulama_kelimeler = [k for k in kelimeler if k not in temizlenecek]
    uygulama_adi = " ".join(uygulama_kelimeler).strip()

    # Sadece fiil kaldıysa veya çok kısa bir şey varsa sor
    if not uygulama_adi or len(uygulama_adi) < 2:
        asistan_mesaj("Hangi uygulamayı açmamı istersin?")
        return

    asistan_mesaj(f"{uygulama_adi.title()} açılıyor...")

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
# YENİ: ÇEVİRİ
# -----------------------------------
def translate_text(command):
    """
    Komut örnekleri:
      "merhaba İngilizceye çevir"
      "hello ne demek"
      "good morning Türkçe söyle"
    """
    try:
        # Yön belirle
        if any(x in command for x in ["ingilizce", "İngilizce", "english"]):
            source, target, lang_label = "tr", "en", "İngilizce"
        else:
            source, target, lang_label = "en", "tr", "Türkçe"

        # Komut kelimelerini temizle
        temizle = ["çevir", "çeviri", "ingilizce", "türkçe", "söyle", "ne", "demek",
                   "translate", "english", "İngilizce", "Türkçe"]
        kelimeler = command.split()
        metin = " ".join([k for k in kelimeler if k.lower() not in [t.lower() for t in temizle]]).strip()

        if not metin:
            asistan_mesaj("Ne çevirmemi istersin?")
            return

        translator = GoogleTranslator(source=source, target=target)
        ceviri = translator.translate(metin)
        asistan_mesaj(f"{lang_label} karşılığı: {ceviri}")

    except Exception as e:
        ui_log(f"[ÇEVİRİ HATASI]: {e}")
        asistan_mesaj("Çeviri sırasında bir sorun oluştu. İnternet bağlantınızı kontrol edin.")

# -----------------------------------
# YENİ: MATEMATİK HESAPLAMA
# -----------------------------------
def calculate(command):
    """
    Türkçe sesli matematik komutlarını işler.
    Örnekler: "beş artı üç hesapla", "on çarpı iki kaç eder", "yüz bölü dört"
    """
    # Türkçe sayı ve operatör dönüşüm tablosu
    sayi_sozlugu = {
        "sıfır": "0", "bir": "1", "iki": "2", "üç": "3", "dört": "4",
        "beş": "5", "altı": "6", "yedi": "7", "sekiz": "8", "dokuz": "9",
        "on": "10", "yirmi": "20", "otuz": "30", "kırk": "40", "elli": "50",
        "altmış": "60", "yetmiş": "70", "seksen": "80", "doksan": "90",
        "yüz": "100", "bin": "1000"
    }
    operatör_sozlugu = {
        "artı": "+", "eksi": "-", "çıkar": "-", "çıkart": "-",
        "çarpı": "*", "çarp": "*", "bölü": "/", "böl": "/",
        "mod": "%", "üssü": "**", "kare": "**2"
    }

    # Temizlik kelimeleri
    temizle = ["hesapla", "kaç", "eder", "eşittir", "sonucu", "nedir", "ne"]
    kelimeler = command.lower().split()
    kelimeler = [k for k in kelimeler if k not in temizle]

    # Türkçe → sembol dönüşümü
    donusturulmus = []
    for k in kelimeler:
        if k in sayi_sozlugu:
            donusturulmus.append(sayi_sozlugu[k])
        elif k in operatör_sozlugu:
            donusturulmus.append(operatör_sozlugu[k])
        elif re.match(r"^\d+[\.,]?\d*$", k):
            donusturulmus.append(k.replace(",", "."))
        else:
            donusturulmus.append(k)

    ifade = " ".join(donusturulmus)

    # Güvenli eval — sadece sayı ve matematiksel operatörlere izin ver
    guvenli_ifade = re.sub(r"[^0-9+\-*/().% ]", "", ifade).strip()

    if not guvenli_ifade:
        asistan_mesaj("Hesaplayabileceğim bir ifade bulamadım. Örnek: beş artı üç hesapla.")
        return

    try:
        sonuc = eval(guvenli_ifade)
        # Ondalık sonuçları düzelt
        if isinstance(sonuc, float) and sonuc == int(sonuc):
            sonuc = int(sonuc)
        asistan_mesaj(f"Sonuç: {sonuc}")
        ui_log(f"   📐 İfade: {guvenli_ifade} = {sonuc}")
    except ZeroDivisionError:
        asistan_mesaj("Bir sayıyı sıfıra bölemezsin.")
    except Exception as e:
        ui_log(f"[MATEMATİK HATASI]: {e}")
        asistan_mesaj("Bu ifadeyi hesaplayamadım.")

# -----------------------------------
# ANA DÖNGÜ
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
        elif niyet == "ceviri":
            translate_text(command)
        elif niyet == "matematik":
            calculate(command)
        elif niyet == "ses_kapat":
            pyautogui.press("volumemute")
            asistan_mesaj("Ses kapatıldı.")
        elif niyet == "ses_ac":
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

# -----------------------------------
# THREAD
# -----------------------------------
def background_listener():
    time.sleep(1)
    ui_log("✅ Sistem hazır. Uyandırılmayı bekliyorum.")
    ui_log("💡 İpucu: 'Asistan' diyerek uyandırın.")
    while True:
        if listen_for_wake_word():
            asistan_mesaj(random.choice(["Efendim?", "Dinliyorum.", "Buradayım."]))
            run_assistant()

threading.Thread(target=background_listener, daemon=True).start()
app.mainloop()