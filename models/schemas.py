# Pydantic kütüphanesinden BaseModel sınıfını import et
# Pydantic: Python'da veri validasyonu ve serileştirme için kullanılan kütüphane
from pydantic import BaseModel

class QueryRequest(BaseModel):
    """
    API endpoint'lerine gelen query isteklerini validate etmek için model
    
    FastAPI bu modeli otomatik olarak:
    1. JSON request body'sini Python objesine çevirir
    2. Veri tiplerini kontrol eder
    3. Gerekli alanların varlığını doğrular
    4. Otomatik API dokümantasyonu oluşturur
    
    Attributes:
        input (str): Kullanıcının AI'ya sorduğu soru veya komut
    """
    input: str  # Zorunlu string alanı - kullanıcı sorusu
