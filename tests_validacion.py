import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env antes de importar nada de Google
load_dotenv()

from src.rag import inicializar_rag
from src.tools import get_weather

def probar_sistema():
    print("Iniciando pruebas del sistema...")

    pdf_path = "data/TENERIFE.pdf"
    if not os.path.exists(pdf_path):
        print("No se encuentra el PDF.")
        return

    # Prueba 1: RAG
    print("\n1. Probando recuperación del RAG...")
    try:
        retriever = inicializar_rag(pdf_path)
        docs = retriever.invoke("¿Qué ver en Anaga?")
        print(f"OK. Se han recuperado {len(docs)} fragmentos del PDF.")
        for d in docs:
            print(f" - Página {d.metadata.get('page')}: {d.page_content[:80]}...")
    except Exception as e:
        print(f"Fallo en RAG: {e}")

    # Prueba 2: Herramienta del tiempo con fecha válida
    print("\n2. Probando herramienta del tiempo (fecha correcta)...")
    try:
        res = get_weather.invoke({"fecha": "2026-08-12"})
        print(f"Resultado: {res}")
    except Exception as e:
        print(f"Fallo: {e}")

    # Prueba 3: Herramienta del tiempo con formato incorrecto (manejo de errores)
    print("\n3. Probando manejo de errores con fecha inválida...")
    try:
        res_error = get_weather.invoke({"fecha": "12-08-2026"})
        print(f"Respuesta controlada: {res_error}")
    except Exception as e:
        print(f"Fallo inesperado: {e}")

if __name__ == "__main__":
    probar_sistema()