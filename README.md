Asistente Turístico de Tenerife — JRPG Edition

Asistente conversacional e interactivo ambientado en los videojuegos de rol de 16 bits (estilo Chrono Trigger), diseñado para ofrecer información turística sobre la isla de Tenerife mediante procesamiento de documentos (RAG) y llamadas a APIs de servicios en tiempo real.

Arquitectura e Integración

El sistema se compone de dos capas principales:

Backend (Python / FastAPI):

Procesamiento de Lenguaje: Google Gemini (gemini-2.0-flash / gemini-1.5-flash) mediante langchain-google-genai.

Gestión de Fuentes (RAG): Carga e inserción en memoria del documento oficial de turismo (data/TENERIFE.pdf) con pypdf.

Integración de Herramientas: Módulo de consulta meteorológica para previsiones puntuales.

Gestión de Estado: Memoria conversacional con ventana flotante para mantener el contexto de los últimos turnos de diálogo.

Frontend (HTML5 / CSS3 / JavaScript):

Interfaz web monolítica inspirada en la estética retro de los menús JRPG.

Comunicación asíncrona mediante peticiones HTTP POST a la API REST de FastAPI.

Instalación y Puesta en Marcha

1. Requisitos previos

Python 3.10+

Clave de API de Google Gemini (Gemini Developer API)

2. Configuración del entorno

Clona el repositorio e instala las dependencias dentro de un entorno virtual:

git clone <URL_DEL_REPOSITO>
cd asistente_turistico_tenerife

python3 -m venv venv
source venv/bin/venv/bin/activate  # En Windows: venv\Scripts\activate

pip install -r requirements.txt


3. Variables de entorno

Crea un archivo .env en la raíz del proyecto e introduce tu clave de API:

GOOGLE_API_KEY=tu_api_key_aqui


4. Estructura de carpetas

Asegúrate de que la estructura del proyecto contiene la guía de la isla en la carpeta data/:

asistente_turistico_tenerife/
├── data/
│   └── TENERIFE.pdf
├── src/
│   ├── config.py
│   ├── memory.py
│   ├── rag.py
│   └── tools.py
├── static/
│   └── index.html
├── server.py
├── .env
└── requirements.txt


5. Ejecución del servidor

Para levantar la aplicación en modo desarrollo:

uvicorn server:app --reload


Accede desde cualquier navegador web a: http://127.0.0.1:8000

Funcionalidades

Consultas sobre la Guía: Preguntas sobre municipios, rutas, gastronomía y puntos de interés de la isla de Tenerife procesadas mediante el contexto extraído de la documentación oficial.

Predicción Meteorológica: Detección de intenciones sobre el clima para ejecutar funciones de consulta ambiental.

Inmersión RPG: Las respuestas del modelo se personalizan con un rol temático (el "Sabio de Tenerife"), manteniendo una estética de caja de texto retro de 16 bits.