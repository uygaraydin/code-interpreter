import os      # İşletim sistemi işlemleri için
import glob    # Dosya arama desenleri için  
from fastapi import UploadFile                    # FastAPI dosya upload tipi
from services.agent_service import clear_csv_agent  # AI agent hafızasını temizleme
from config.settings import UPLOAD_DIR, ensure_upload_dir  # Ayarlar

def get_current_csv():
    """
    Mevcut CSV dosyasının adını al
    
    Returns:
        str or None: CSV dosya adı varsa, yoksa None
    """
    # Upload dizini mevcut mu kontrol et
    if os.path.exists(UPLOAD_DIR):
        # uploads/*.csv desenine uyan tüm dosyaları bul
        csv_files = glob.glob(f"{UPLOAD_DIR}/*.csv")
        
        # En az bir CSV dosyası varsa
        if csv_files:
            # İlk dosyanın sadece adını döndür (tam path değil)
            # Örnek: "/uploads/data.csv" -> "data.csv"
            return os.path.basename(csv_files[0])
    
    # Hiç CSV yoksa None döndür
    return None

async def upload_csv_file(file: UploadFile):
    """
    CSV dosyası yükle ve kaydet
    
    Args:
        file (UploadFile): Yüklenen dosya objesi
    
    Returns:
        dict: Sonuç mesajı ve dosya yolu
    """
    # Dosya uzantısı kontrolü - sadece .csv kabul et
    if not file.filename.endswith('.csv'):
        return {"error": "Sadece CSV dosyaları yüklenebilir"}
    
    # Upload dizininin var olduğundan emin ol
    ensure_upload_dir()
    
    # Önceki CSV dosyalarını temizle (tek seferde bir CSV)
    # Bu uygulama sadece bir CSV ile çalışacak şekilde tasarlanmış
    for old_file in glob.glob(f"{UPLOAD_DIR}/*.csv"):
        os.remove(old_file)
    
    # Yeni dosyayı kaydetme işlemi
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    
    # Dosyayı binary modda aç ve yaz
    with open(file_path, "wb") as buffer:
        # FastAPI UploadFile'dan içeriği oku
        content = await file.read()
        # Diske yaz
        buffer.write(content)
    
    # Başarılı sonuç döndür
    return {"message": "CSV dosyası başarıyla yüklendi", "path": file_path}

def remove_all_csv_files():
    """
    Tüm CSV dosyalarını sil ve AI hafızasını temizle
    
    Returns:
        dict: İşlem sonucu mesajı
    """
    # Upload dizini var mı kontrol et
    if os.path.exists(UPLOAD_DIR):
        # Tüm CSV dosyalarını bul ve sil
        for csv_file in glob.glob(f"{UPLOAD_DIR}/*.csv"):
            os.remove(csv_file)
    
    # AI agent'ının CSV hafızasını da temizle
    # Bu önemli: fiziksel dosya silinse de AI hafızada kalabilir
    clear_csv_agent()
    
    return {"message": "CSV dosyası kaldırıldı"}

def cleanup_uploads():
    """
    Upload dizinini tamamen temizle
    Uygulama kapanırken çalışır (atexit ile kayıtlı)
    """
    if os.path.exists(UPLOAD_DIR):
        # Tüm CSV dosyalarını sil
        for csv_file in glob.glob(f"{UPLOAD_DIR}/*.csv"):
            os.remove(csv_file)