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

   
## Week 3: Core Assistant Mechanics & System Integration

Bu hafta, masaüstü asistanının temel iskeleti oluşturuldu ve işletim sistemiyle etkileşime giren çekirdek komutlar kodlandı. Geliştirme ve test süreçlerinin daha hızlı/hatasız ilerleyebilmesi adına, asistanın yanıtları bu aşamada doğrudan **terminal (console) çıktılarına** yönlendirilmiştir.

### 🚀 Eklenen Yeni Özellikler (Features)

*   **Sesli Komut Algılama (Speech-to-Text):** `speech_recognition` kütüphanesi kullanılarak kullanıcının mikrofon üzerinden verdiği sesli komutlar metne (string) dönüştürüldü.
*   **Sistem Komutları (System Commands):** 
    *   `datetime` modülü ile bilgisayarın yerel saati ve tarihi çekilerek kullanıcıya sunuldu.
    *   Asistana temel sohbet yetenekleri (selamlama, hal hatır sorma) eklendi.
*   **Uygulama ve Tarayıcı Otomasyonu (Open Applications):**
    *   `os.system` modülü kullanılarak dış bir bağımlılık olmadan Windows yerleşik programlarının (Notepad, Calc) ve Spotify'ın başlatılması sağlandı.
    *   `webbrowser` modülü kullanılarak Google, YouTube ve önceden belirlenmiş medya linklerinin varsayılan tarayıcıda açılması sağlandı.
*   **Dış API Entegrasyonu (Weather API):**
    *   OpenWeatherMap API kullanılarak sisteme hava durumu yeteneği kazandırıldı. Sesli komutun içinden şehir ismi ayrıştırılıp, `requests` modülü ile anlık sıcaklık ve hava durumu bilgisi çekildi.
*   **Kontrollü Çıkış (Graceful Exit):** Asistanın arka planda sonsuz döngüde çalışmasını durdurmak için ("kapat", "çıkış yap" gibi) terminal komutlarıyla sistemi sonlandırma eklendi.

### 🛠️ Kullanılan Teknolojiler ve Kütüphaneler (Dependencies)
*   **Harici Kütüphaneler:** `SpeechRecognition`, `PyAudio` (Mikrofon erişimi için), `requests` (API HTTP çağrıları için).
*   **Standart Kütüphaneler:** `os`, `datetime`, `webbrowser`, `random`, `time`.

