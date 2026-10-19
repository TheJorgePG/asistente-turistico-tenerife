from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

from src.tools import get_weather
from src.memory import ConversationalMemory
from src.config import Config
from src.rag import inicializar_rag
from langchain_google_genai import ChatGoogleGenerativeAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializamos el RAG al arrancar la app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(BASE_DIR, "data", "TENERIFE.pdf")

retriever = None
if os.path.exists(pdf_path):
    try:
        retriever = inicializar_rag(pdf_path)
        print("Vector store cargado correctamente.")
    except Exception as e:
        print(f"Error al cargar el RAG: {e}")

memory = ConversationalMemory(max_turns=10)

# Configuramos el modelo y le enlazamos la herramienta
llm = ChatGoogleGenerativeAI(model=Config.MODEL_NAME, temperature=0.7)
llm_with_tools = llm.bind_tools([get_weather])

class MessageRequest(BaseModel):
    message: str

@app.post("/api/interact")
def interact(req: MessageRequest):
    user_msg = req.message.strip()
    memory.add_message("user", user_msg)
    
    try:
        # Detectamos si pide el tiempo para usar la herramienta con argumentos
        palabras_clima = ["tiempo", "clima", "lluvia", "temperatura", "meteorología"]
        if any(p in user_msg.lower() for p in palabras_clima):
            messages = [
                ("system", "Eres un guía de Tenerife. Usa la herramienta del clima si el usuario pregunta por la meteorología, extrayendo la fecha en formato YYYY-MM-DD."),
                ("user", user_msg)
            ]
            response = llm_with_tools.invoke(messages)
            
            if response.tool_calls:
                tool_call = response.tool_calls[0]
                tool_args = tool_call.get("args", {})
                weather_result = get_weather.invoke(tool_args)
                reply = f"Previsión meteorológica: {weather_result}"
            else:
                reply = response.content
                
        elif retriever:
            # Búsqueda real en el vector store
            docs_relevantes = retriever.invoke(user_msg)
            contexto_rag = "\n\n".join([f"[Página {doc.metadata.get('page', 'N/D')}]: {doc.page_content}" for doc in docs_relevantes])
            
            prompt = (
                "Responde al viajero usando únicamente la siguiente información de la guía oficial de Tenerife. "
                "Cita la fuente o número de página al final.\n\n"
                f"Información de la guía:\n{contexto_rag}\n\n"
                f"Pregunta: {user_msg}"
            )
            
            response = llm.invoke(prompt)
            reply = response.content
        else:
            reply = "La guía no está disponible en este momento."
            
    except Exception as e:
        reply = f"Ha ocurrido un error: {str(e)}"
        
    memory.add_message("assistant", reply)
    return {"reply": reply}

app.mount("/", StaticFiles(directory="static", html=True), name="static")