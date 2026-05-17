

import speech_recognition as sr
import datetime
import os
import random
import requests
import time
from gtts import gTTS
from playsound import playsound
import wikipedia
import pyautogui
import feedparser

# -----------------------------------
# AYARLAR
# -----------------------------------

API_KEY = "b8768819961d2139e8acbafc2ad8c1f2"

DEMO_MODE = False

listener = sr.Recognizer()

listener.pause_threshold = 0.5
listener.dynamic_energy_threshold = True
listener.energy_threshold = 300

# -----------------------------------
# KOMUTLAR
# -----------------------------------

KOMUTLAR = {
    "selamlasma": [
        "merhaba", "selam", "naber", "nasılsın",
        "ne haber", "napıyosun", "hey"
    ],

    "saat": [
        "saat kaç", "saat", "zaman nedir"
    ],

    "tarih": [
        "bugün tarih ne", "tarih", "ayın kaçı"
    ],

    "saka": [
        "şaka yap", "beni güldür", "espri yap"
    ],

    "hava": [
        "hava durumu", "hava nasıl", "kaç derece"
    ],

    "bilgi": [
        "kimdir", "nedir", "hakkında bilgi", "araştır"
    ],

    "haber": [
        "haberler", "gündem", "son dakika"
    ],

    "yazi_tura": [
        "yazı tura", "para at"
    ],

    "zar": [
        "zar at", "zar salla"
    ],

    "ekran_goruntusu": [
        "ekran görüntüsü", "ss al"
    ],

    "ses_kapat": [
        "sesi kapat", "sessize al"
    ],

    "ses_ac": [
        "sesi aç"
    ],

    "ses_yukselt": [
        "ses yükselt", "ses arttır"
    ],

    "ses_kis": [
        "sesi kıs", "sesi azalt"
    ],

    "uygulama_ac": [
        "aç", "başlat", "çalıştır"
    ],

    "cikis": [
        "kapat", "uyu", "görüşürüz",
        "baybay", "çıkış yap"
    ]
}

# -----------------------------------
# SES MOTORU
# -----------------------------------

def speak(text):
    try:
        dosya_adi = "asistan_ses.mp3"

        if os.path.exists(dosya_adi):
            os.remove(dosya_adi)

        tts = gTTS(text=text, lang='tr', slow=False)
        tts.save(dosya_adi)

        playsound(dosya_adi, block=True)

        time.sleep(0.2)

        if os.path.exists(dosya_adi):
            os.remove(dosya_adi)

    except Exception as e:
        print(f"\n[SES HATASI]: {e}")

def asistan_mesaj(text):
    print(f"\nAsistan: {text}")
    speak(text)

# -----------------------------------
# DİNLEME
# -----------------------------------

is_noise_adjusted = False

def take_command(
    mesaj="Dinleniyor...",
    timeout_suresi=8,
    limit_suresi=15
):
    global is_noise_adjusted

    command = ""

    try:
        with sr.Microphone() as source:

            if not is_noise_adjusted:
                print("\n[Ortam sesi ayarlanıyor...]")
                listener.adjust_for_ambient_noise(source, duration=1)
                is_noise_adjusted = True

            print(f"\n{mesaj}")

            audio = listener.listen(
                source,
                timeout=timeout_suresi,
                phrase_time_limit=limit_suresi
            )

            command = listener.recognize_google(
                audio,
                language="tr-TR"
            ).lower()

            print(f"Sen: {command}")

    except sr.WaitTimeoutError:
        pass

    except sr.UnknownValueError:
        pass

    except Exception as e:
        print(f"\n[MİKROFON HATASI]: {e}")

    return command.strip()

# -----------------------------------
# WAKE WORD
# -----------------------------------

WAKE_WORDS = [
    "hey asistan",
    "asistan"
]

def listen_for_wake_word():

    print("\n[Uyandırma Kelimesi Bekleniyor]")

    command = take_command(
        mesaj="...",
        timeout_suresi=5,
        limit_suresi=5
    )

    return any(
        wake_word in command
        for wake_word in WAKE_WORDS
    )

# -----------------------------------
# INTENT BUL
# -----------------------------------

def intent_bul(command):

    for niyet, kelimeler in KOMUTLAR.items():

        if any(
            kelime in command
            for kelime in kelimeler
        ):
            return niyet

    return None

# -----------------------------------
# YARDIMCI FONKSİYONLAR
# -----------------------------------

def tell_time():

    now = datetime.datetime.now()

    asistan_mesaj(
        "Şu an saat " +
        now.strftime("%H:%M")
    )

def tell_date():

    now = datetime.datetime.now()

    asistan_mesaj(
        "Bugünün tarihi " +
        now.strftime("%d.%m.%Y")
    )

def tell_joke():

    jokes = [
        "Yazılımcının sevgilisi neden ayrılmış? Çünkü adam her tartışmada sistemde bug var demiş.",

        "İki bit yolda karşılaşıyor. Biri diyor ki sıfırın altındayım kardeşim."
    ]

    asistan_mesaj(random.choice(jokes))

def get_city(command):

    # Önce tam kelime gruplarını temizle ("hava durumu", "hava nasıl" vb.)
    for kalip in KOMUTLAR["hava"]:
        command = command.replace(kalip, "")

    temizlenecek_ekstra = ["da", "de", "için", "söyle", "hava"]

    kelimeler = command.split()

    city_words = [
        k for k in kelimeler
        if k not in temizlenecek_ekstra
    ]

    city = " ".join(city_words).strip()

    return city.title() if city else "Ankara"

def weather(city):

    try:

        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={city}&appid={API_KEY}&units=metric&lang=tr"
        )

        response = requests.get(url)

        data = response.json()

        if data["cod"] != 200:
            asistan_mesaj("Şehri bulamadım.")
            return

        derece = data["main"]["temp"]
        durum = data["weather"][0]["description"]

        asistan_mesaj(
            f"{city} için hava {durum}. "
            f"Sıcaklık {round(derece)} derece."
        )

    except:
        asistan_mesaj("Hava durumunu çekemedim.")

# -----------------------------------
# ANA ASİSTAN
# -----------------------------------

def run_assistant():

    while True:

        command = take_command(
            mesaj="Seni dinliyorum...",
            timeout_suresi=8,
            limit_suresi=15
        )

        # Sessizlik varsa devam et
        if len(command) < 2:
            continue

        niyet = intent_bul(command)

        # -----------------------------------

        if niyet == "selamlasma":

            cevaplar = [
                "Merhaba kral.",
                "Buradayım kral.",
                "Seni dinliyorum.",
                "Nasıl yardımcı olayım?"
            ]

            asistan_mesaj(random.choice(cevaplar))

        # -----------------------------------

        elif niyet == "saat":
            tell_time()

        elif niyet == "tarih":
            tell_date()

        elif niyet == "saka":
            tell_joke()

        # -----------------------------------

        elif niyet == "hava":

            city = get_city(command)

            weather(city)

        # -----------------------------------

        elif niyet == "bilgi":

            search_term = command

            for word in KOMUTLAR["bilgi"]:
                search_term = search_term.replace(word, "")

            search_term = search_term.strip()

            if not search_term:
                asistan_mesaj("Neyi araştırmamı istediğini anlayamadım.")
                continue

            # Wikipedia'nın botları engellememesi için bir kimlik (User-Agent) tanımlıyoruz
            wikipedia.set_user_agent("AsistanBot/1.0")
            wikipedia.set_lang("tr")

            try:

                # Önce aranan kelimenin Wikipedia'daki en yakın başlığını arıyoruz
                search_results = wikipedia.search(search_term)
                
                if not search_results:
                    asistan_mesaj("Bununla ilgili bilgi bulamadım.")
                    continue
                    
                en_iyi_sonuc = search_results[0]

                asistan_mesaj(
                    f"{en_iyi_sonuc} için araştırıyorum."
                )

                result = wikipedia.summary(
                    en_iyi_sonuc,
                    sentences=2,
                    auto_suggest=False
                )

                asistan_mesaj(result)

            except wikipedia.exceptions.DisambiguationError:

                asistan_mesaj(
                    "Birden fazla sonuç çıktı. "
                    "Biraz daha net söyler misin?"
                )

            except wikipedia.exceptions.PageError:

                asistan_mesaj(
                    "Bununla ilgili bilgi bulamadım."
                )

            except Exception as e:

                asistan_mesaj(
                    "Wikipedia tarafında bir hata oluştu."
                )
                print(f"\n[WİKİPEDİA HATASI]: {e}")

        # -----------------------------------

        elif niyet == "haber":

            try:

                asistan_mesaj(
                    "Güncel haberleri okuyorum."
                )

                feed = feedparser.parse(
                    "https://www.trthaber.com/manset_articles.rss"
                )

                for i in range(3):

                    asistan_mesaj(
                        feed.entries[i].title
                    )

                    time.sleep(0.5)

            except:

                asistan_mesaj(
                    "Haberlere ulaşamadım."
                )

        # -----------------------------------

        elif niyet == "yazi_tura":

            sonuc = random.choice([
                "Yazı",
                "Tura"
            ])

            asistan_mesaj(
                f"Sonuç: {sonuc}"
            )

        # -----------------------------------

        elif niyet == "zar":

            sonuc = random.randint(1, 6)

            asistan_mesaj(
                f"Gelen sayı: {sonuc}"
            )

        # -----------------------------------

        elif niyet == "ekran_goruntusu":

            if DEMO_MODE:

                asistan_mesaj(
                    "Demo modunda ekran görüntüsü alınmadı."
                )

            else:

                dosya_adi = (
                    f"ekran_{int(time.time())}.png"
                )

                pyautogui.screenshot(dosya_adi)

                asistan_mesaj(
                    "Ekran görüntüsü alındı."
                )

        # -----------------------------------

        elif niyet == "uygulama_ac":

            app_name = command

            for word in KOMUTLAR["uygulama_ac"]:
                app_name = app_name.replace(word, "")

            app_name = app_name.strip()

            if not app_name:

                asistan_mesaj(
                    "Hangi uygulamayı açayım?"
                )

                continue

            asistan_mesaj(
                f"{app_name} açılıyor."
            )

            pyautogui.press("win")

            time.sleep(0.5)

            pyautogui.typewrite(app_name)

            time.sleep(0.5)

            pyautogui.press("enter")

        # -----------------------------------

        elif niyet == "ses_kapat":

            if not DEMO_MODE:
                pyautogui.press("volumemute")

            asistan_mesaj("Ses kapatıldı.")

        # -----------------------------------

        elif niyet == "ses_ac":

            if not DEMO_MODE:
                pyautogui.press("volumemute")

            asistan_mesaj("Ses açıldı.")

        # -----------------------------------

        elif niyet == "ses_yukselt":

            if not DEMO_MODE:

                for _ in range(10):
                    pyautogui.press("volumeup")

            asistan_mesaj(
                "Ses yükseltildi."
            )

        # -----------------------------------

        elif niyet == "ses_kis":

            if not DEMO_MODE:

                for _ in range(10):
                    pyautogui.press("volumedown")

            asistan_mesaj(
                "Ses düşürüldü."
            )

        # -----------------------------------

        elif niyet == "cikis":

            asistan_mesaj(
                "Tamam kral. Tekrar çağırırsan buradayım."
            )

            return True

        # -----------------------------------

        else:

            asistan_mesaj(
                "Bunu anlayamadım. "
                "Farklı şekilde söyler misin?"
            )

# -----------------------------------
# BAŞLANGIÇ
# -----------------------------------

print("-----------------------------------")

asistan_mesaj(
    "Sistem hazır. Uyandırılmayı bekliyorum."
)

print("-----------------------------------")

while True:

    if listen_for_wake_word():

        asistan_mesaj(
            random.choice([
                "Efendim?",
                "Dinliyorum.",
                "Buradayım."
            ])
        )

        run_assistant()