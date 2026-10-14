import os
import sys
from src.config import Config
from src.rag import inicializar_rag
from src.memory import ConversationalMemory
from src.tools import get_weather

def main():
    print("==================================================")
    print("      ASISTENTE TURÍSTICO INTELIGENTE - TENERIFE   ")
    print("==================================================")
    
    # 1. Verificación inicial de la clave de API
    if not Config.GOOGLE_API_KEY:
        print("[ERROR] No se ha encontrado la GOOGLE_API_KEY en el archivo .env.")
        sys.exit(1)

    print(f"-> Modelo activo: {Config.MODEL_NAME}")
    print("-> Inicializando base de conocimientos (RAG)...")
    
    # 2. Carga del pipeline RAG con la guía de Tenerife
    pdf_path = "data/TENERIFE.pdf"
    if not os.path.exists(pdf_path):
        print(f"[ERROR] No se encuentra la guía turística en '{pdf_path}'. Colócala ahí para continuar.")
        sys.exit(1)
        
    try:
        retriever = inicializar_rag(pdf_path)
        print("-> Guía indexada correctamente en el Vector Store.")
    except Exception as e:
        print(f"[ERROR] Fallo al inicializar el RAG: {e}")
        sys.exit(1)

    # 3. Inicialización de la memoria multiturno
    memory = ConversationalMemory(max_turns=5)
    
    print("\n¡Asistente listo! Escribe tus dudas sobre Tenerife (ej. '¿Qué ver en La Orotava?' o '¿Qué tiempo hace?').")
    print("Escribe 'salir' para terminar la ejecución.\n")

    # 4. Bucle principal de conversación
    while True:
        try:
            pregunta = input("Usuario: ").strip()
            if not pregunta:
                continue
            
            if pregunta.lower() in ["salir", "exit", "quit"]:
                print("\n¡Gracias por utilizar el asistente turístico de Tenerife. ¡Hasta pronto!")
                break
            
            # Registrar mensaje del usuario en memoria
            memory.add_message("user", pregunta)
            
            # Detección y ejecución de herramientas (Function Calling obligatorio)
            if "tiempo" in pregunta.lower() or "clima" in pregunta.lower():
                # Simulamos o extraemos la fecha (por defecto usaremos una de prueba)
                fecha_prueba = "2026-06-15"
                print(sys.stdout.write(f"\n[Sistema] Ejecutando herramienta externa get_weather('{fecha_prueba}')...\n"))
                resultado_clima = get_weather(fecha_prueba)
                respuesta = f"Según la previsión meteorológica para la fecha {fecha_prueba}: {resultado_clima}"
            else:
                # Búsqueda semántica mediante RAG
                docs_relevantes = retriever.invoke(pregunta)
                contexto_rag = "\n".join([doc.page_content for doc in docs_relevantes])
                
                # Respuesta basada en el contexto recuperado de la guía
                respuesta = (
                    f"Consultando la guía oficial de Tenerife...\n\n"
                    f"Información relevante encontrada:\n{contexto_rag[:600]}...\n\n"
                    f"(Fuente: Guía turística oficial de Tenerife)"
                )
            
            # Registrar respuesta del asistente en memoria
            memory.add_message("assistant", respuesta)
            print(f"\nAsistente:\n{respuesta}\n" + "-"*50)

        except KeyboardInterrupt:
            print("\n\nSesión interrumpida. ¡Hasta luego!")
            break

if __name__ == "__main__":
    main()