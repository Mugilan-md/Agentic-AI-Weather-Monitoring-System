import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Config:
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
    
    # Open-Meteo Endpoints (Free, no API key required)
    OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    OPEN_METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
