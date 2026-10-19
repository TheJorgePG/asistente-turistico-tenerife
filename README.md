# Asistente Turístico de Tenerife — JRPG Edition

Asistente conversacional e interactivo ambientado en los videojuegos de rol de 16 bits (estilo Chrono Trigger), diseñado para ofrecer información turística sobre la isla de Tenerife mediante recuperación documental (RAG) y llamadas dinámicas a herramientas (*Tool Calling*).

---

## Justificación Técnica y Decisiones de Diseño

En respuesta a la revisión de requisitos, se han ajustado las partes clave del sistema priorizando su correcto funcionamiento y robustez:

### 1. Sistema RAG (Indexación y Recuperación Semántica)
- **Qué se ha hecho:** Se construyó un pipeline RAG completo en `src/rag.py` que fragmenta la guía oficial (`data/TENERIFE.pdf`) con `RecursiveCharacterTextSplitter` e indexa los fragmentos en una base de datos vectorial **ChromaDB** (`data/chroma_db`).
- **Por qué se tomó esta decisión:** Se eligió el modelo de embeddings local `all-MiniLM-L6-v2` (`sentence-transformers`) para eliminar la dependencia de la API de embeddings de Google, evitando límites de cuota, bloqueos o errores de red. La persistencia en disco con ChromaDB evita recalcular los vectores en cada inicio del servidor.
- **Resultados obtenidos:** Búsquedas por similitud precisas (`k=3`) que recuperan los fragmentos relevantes según la pregunta del usuario y fuerzan al modelo a citar la fuente y el número de página exacto.

### 2. Herramienta Meteorológica Dinámica (*Tool Calling*)
- **Qué se ha hecho:** Se implementó la función `get_weather` en `src/tools.py` decorada con `@tool` y respaldada por un esquema de **Pydantic** (`WeatherInput`) para la validación de la fecha (`YYYY-MM-DD`). La herramienta se vincula al LLM con `.bind_tools()`.
- **Por qué se tomó esta decisión:** Se eliminó la detección rígida por palabras clave o fechas fijas (*hardcoded*). Ahora es el modelo de lenguaje el que interpreta la intención del usuario, infiere la fecha correspondiente y llama autónomamente a la herramienta pasando los argumentos extraídos.
- **Resultados obtenidos:** Ejecución dinámica de herramientas con validación estricta de parámetros y captura controlada de excepciones ante entradas no válidas.

### 3. Suite de Pruebas de Validación
- **Qué se ha hecho:** Se creó el script `tests_validacion.py` en la raíz del proyecto para automatizar las pruebas unitarias e integradas del sistema.
- **Por qué se tomó esta decisión:** Permite comprobar de forma aislada y rápida, sin necesidad de levantar el servidor web, que la recuperación vectorial funciona, que las herramientas responden correctamente y que los errores de formato o cuota se gestionan sin colapsar la aplicación.
- **Resultados obtenidos:** Verificación automatizada con paso del 100% de los tests de validación.

---

## Arquitectura del Sistema

El sistema se compone de dos capas principales:

### Backend (Python / FastAPI)
- **Procesamiento de Lenguaje:** Google Gemini integrado mediante `langchain-google-genai`.
- **Gestión de Fuentes:** Motor RAG sobre ChromaDB con embeddings locales de HuggingFace.
- **Herramientas:** Consulta meteorológica validada con Pydantic y llamada autónoma vía `.bind_tools()`.
- **Gestión de Estado:** Memoria conversacional por ventana flotante para mantener el contexto del diálogo.

### Frontend (HTML5 / CSS3 / JavaScript)
- Interfaz monolítica de página única con estética retro de menús JRPG de 16 bits.
- Peticiones asíncronas HTTP POST a la API REST de FastAPI con saneamiento explícito de datos para evitar errores de renderizado de objetos (`[object Object]`).

---

## Instalación y Puesta en Marcha

### 1. Requisitos previos
- Python 3.10+
- Clave de API de Google Gemini

### 2. Configuración del entorno
```bash
git clone <URL_DEL_REPOSITORIO>
cd asistente_turistico_tenerife

python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

pip install -r requirements.txt

### 3. Ejecución de pruebas
python tests_validacion.py

### 4. Ejecución del servidor
uvicorn server:app --reload

http://127.0.0.1:8000