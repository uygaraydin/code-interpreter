# Sistem kütüphanelerini import et
import os                    # İşletim sistemi işlemleri için
from dotenv import load_dotenv  # .env dosyasından environment variables okumak için

# .env dosyasındaki değişkenleri yükle
# Bu dosyada API key'ler, veritabanı şifreleri gibi gizli bilgiler saklanır
load_dotenv()

# FASTAPI SUNUCU AYARLARI
HOST = "0.0.0.0"           # Tüm network interface'lerden erişime izin ver
                           # "127.0.0.1" sadece local, "0.0.0.0" dış erişim
PORT = int(os.environ.get("PORT", 8000))   
             # HTTP port numarası
SECRET_KEY = "my-secret-key-123"  # Session encryption için gizli anahtar
                                  # Üretimde güçlü, rastgele bir key kullanılmalı

# AI MODEL AYARLARI  
OPENAI_MODEL = "gpt-4"     # Kullanılacak OpenAI model adı
                           # Diğer seçenekler: "gpt-3.5-turbo", "gpt-4-turbo"

# DOSYA YÜKLEME AYARLARI
UPLOAD_DIR = "uploads"     # CSV dosyalarının kaydedileceği klasör
                           # Güvenlik: web root dışında olmalı

# TEMPLATE AYARLARI
TEMPLATE_DIR = "templates"  # Jinja2 HTML şablonlarının konumu

# UTILITY FONKSIYON
def ensure_upload_dir():
    """
    Upload dizininin var olduğundan emin ol
    
    Uygulama başlarken çağrılır. Eğer klasör yoksa oluşturur.
    Dosya yükleme hatalarını önlemek için gerekli.
    """
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)  # Klasörü ve parent klasörleri oluştur