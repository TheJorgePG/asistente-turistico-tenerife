import json
import logging
from datetime import datetime
from pydantic import BaseModel, Field

logging.basicConfig(
    filename='logs/execution.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WeatherInput(BaseModel):
    fecha: str = Field(description="Fecha en formato YYYY-MM-DD para la predicción meteorológica.")

def get_weather(fecha: str) -> str:
    """
    Función externa que devuelve la predicción del tiempo en Tenerife con gestión de errores básica.
    """
    logging.info(f"Intento de llamada a get_weather con fecha: {fecha}")
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        
        # Simulación basada en los microclimas de la guía de Tenerife
        weather_data = {
            "estado": "Soleado con nubes dispersas en la costa norte",
            "temperatura_media": "24°C",
            "probabilidad_lluvia": "10%",
            "recomendacion": "Ideal para visitar el Parque Rural de Anaga o la Playa de Benijo."
        }
        logging.info(f"get_weather ejecutada con éxito para la fecha {fecha}")
        return json.dumps(weather_data, ensure_ascii=False)
    
    except ValueError as e:
        error_msg = f"Error de validación en la fecha '{fecha}': Formato incorrecto. Use YYYY-MM-DD."
        logging.error(error_msg)
        return json.dumps({"error": error_msg})
    except Exception as e:
        error_msg = f"Error inesperado en servicio meteorológico: {str(e)}"
        logging.error(error_msg)
        return json.dumps({"error": error_msg})