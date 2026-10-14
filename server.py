from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from src.tools import get_weather
from src.memory import ConversationalMemory
from src.config import Config
from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Extraer el texto del PDF directamente al arrancar la aplicación
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(BASE_DIR, "data", "TENERIFE.pdf")

texto_guia = ""
if os.path.exists(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                texto_guia += t + "\n"
        print(f"-> [OK] PDF leído correctamente en memoria. Caracteres totales: {len(texto_guia)}")
    except Exception as e:
        print(f"-> [ERROR] No se pudo leer el PDF: {e}")
else:
    print(f"-> [CRÍTICO] No se encuentra el PDF en: {pdf_path}")

memory = ConversationalMemory(max_turns=10)
llm = ChatGoogleGenerativeAI(model=Config.MODEL_NAME, temperature=0.7)

class MessageRequest(BaseModel):
    message: str

@app.post("/api/interact")
def interact(req: MessageRequest):
    user_msg = req.message.strip()
    memory.add_message("user", user_msg)
    
    print(f"\n[DEBUG] Mensaje recibido: '{user_msg}'")
    
    # 1. Comprobación de Herramienta (Clima)
    palabras_clima = ["tiempo", "clima", "lluvia", "temperatura", "meteorología"]
    if any(p in user_msg.lower() for p in palabras_clima):
        weather = get_weather("2026-06-15")
        reply = f"🌦️ [MAGIA METEOROLÓGICA]: El clima en Tenerife indica: {weather}"
    
    # 2. Búsqueda directa en el texto de la guía y Gemini
    elif texto_guia:
        try:
            # Seleccionar un fragmento relevante o pasar una porción clave del texto
            historial = "\n".join([f"{m['role']}: {m['content']}" for m in memory.get_context()[-4:]])
            
            prompt_sistema = (
                "Eres un sabio consejero y guía turístico de una isla mística inspirada en Tenerife, "
                "con la estética y tono de un juego de rol clásico (tipo Chrono Trigger). "
                "Utiliza la siguiente información oficial de la guía para responder al viajero de forma mágica, concisa y útil:\n\n"
                f"--- INFORMACIÓN DE LA GUÍA (Extracto) ---\n{texto_guia[:15000]}\n-----------------------------------------\n\n"
                f"Historial reciente:\n{historial}\n\n"
                f"Pregunta del viajero: {user_msg}"
            )
            
            response = llm.invoke(prompt_sistema)
            reply = f"📜 {response.content}"
        except Exception as e:
            print(f"[DEBUG] Error al invocar LLM: {e}")
            reply = f"⚠️ [ERROR ARCANO]: Fallo al consultar los pergaminos: {str(e)}"
    else:
        reply = "⚠️ El sabio medita en silencio... (La guía de Tenerife no está disponible en memoria)."
        
    memory.add_message("assistant", reply)
    return {"reply": reply}

# Servir el frontend estático
app.mount("/", StaticFiles(directory="static", html=True), name="static")