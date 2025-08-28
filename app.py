# Gerekli kütüphaneleri import et
from fastapi import FastAPI, Request, Form, UploadFile, File
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
import atexit

# Kendi modüllerimizden gerekli ayarları import et
from config.settings import HOST, PORT, SECRET_KEY, TEMPLATE_DIR
from models.schemas import QueryRequest
from services.agent_service import router_agent_executor, conversation_memory, update_csv_agent
from services.file_service import get_current_csv, upload_csv_file, remove_all_csv_files, cleanup_uploads

# FastAPI uygulamasını başlat
app = FastAPI()

# Jinja2 template engine'i kurulum - HTML şablonlarını render etmek için
templates = Jinja2Templates(directory=TEMPLATE_DIR)

"""Ana sayfayı açar, session/hafızayı temizler, sayfayı HTML olarak döner."""
# ANA SAYFA - GET isteği ile erişilen web arayüzü
@app.get("/", response_class=HTMLResponse) #Endpoint’in HTML içerik döndüreceğini FastAPI’ye bildiriyorsun.
async def web_interface(request: Request):
    # Her ana sayfa yüklemesinde session'ı temizle - yeni başlangıç için
    request.session.clear()
    
    # AI agent'ının konuşma hafızasını da temizle
    conversation_memory.clear()
    
    # URL parametrelerinden durum mesajlarını al
    # Örnek: /?uploaded=success veya /?error=csv_format
    uploaded = request.query_params.get("uploaded")
    error = request.query_params.get("error")
    removed = request.query_params.get("removed")
    
    # Şu anda yüklü olan CSV dosyasının adını al
    current_csv = get_current_csv()
    
    # HTML template'i render et ve kullanıcıya gönder
    return templates.TemplateResponse("index.html", {
        "request": request,                    # Jinja2 için gerekli
        "current_csv": current_csv,            # Yüklü CSV dosya adı
        "csv_uploaded": uploaded == "success", # Başarılı yükleme durumu
        "csv_error": "Sadece CSV dosyaları yüklenebilir" if error == "csv_format" else None,
        "csv_removed": removed == "success"    # Dosya kaldırma durumu
    })

"""JSON formatında gelen API isteklerini alır, agent’a iletir, JSON cevabı döner.
 JSON ile string alır, JSON ile string döner."""
# API ENDPOINT - JSON formatında query işleme (AJAX çağrıları için)
@app.post("/query")
async def process_query(request: QueryRequest):
    # AI agent'ını çalıştır ve cevap al
    # Konuşma hafızası otomatik olarak agent içinde yönetiliyor
    result = router_agent_executor.invoke({"input": request.input})
    
    # JSON formatında cevabı döndür
    return {"output": result["output"]}

# Session yönetimi için middleware ekle - kullanıcı oturumlarını takip etmek için
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

"""Web formundan gelen input’u alır, session’da saklar, agent’a iletir, sohbet geçmişiyle HTML cevabı döner.
formdan string alır, HTML sayfa döner."""
# WEB FORM ENDPOINT - HTML form'undan gelen sorguları işle
@app.post("/web-query", response_class=HTMLResponse)
async def web_query(request: Request, input: str = Form(...)):
    # Session'dan önceki mesajları al (sohbet geçmişi)
    messages = request.session.get("messages", [])
    
    # AI agent'ını çalıştır ve cevap al
    result = router_agent_executor.invoke({"input": input})
    
    # Yeni soru-cevap çiftini mesaj geçmişine ekle
    messages.append({
        "user": input,              # Kullanıcının sorusu
        "bot": result["output"]     # AI'ın cevabı
    })
    
    # Güncellenmiş mesaj geçmişini session'a kaydet
    request.session["messages"] = messages
    
    # Mevcut CSV dosyası durumunu kontrol et
    current_csv = get_current_csv()
    
    # Güncellenmiş sayfayı render et ve döndür
    return templates.TemplateResponse("index.html", {
        "request": request,
        "messages": messages,       # Tüm sohbet geçmişi
        "current_csv": current_csv
    })

# CSV DOSYASI YÜKLEME ENDPOINT
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    # Dosyayı upload et ve sonucu al
    result = await upload_csv_file(file)
    
    # Eğer yükleme başarılıysa (hata yoksa)
    if "error" not in result:
        # AI agent'ının CSV analiz özelliğini yeni dosya ile güncelle
        update_csv_agent(result["path"])
    
    # Yükleme sonucunu JSON olarak döndür
    return result

# CSV DOSYASI KALDIRMA ENDPOINT
@app.post("/remove-csv")
async def remove_csv():
    # Tüm CSV dosyalarını sil ve AI agent'ının CSV hafızasını temizle
    return remove_all_csv_files()

# Uygulama kapanırken dosyaları temizle
# Program sonlandığında otomatik olarak çalışır
atexit.register(cleanup_uploads)

# Ana çalıştırma bloğu - script direkt çalıştırılırsa sunucuyu başlat
if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)