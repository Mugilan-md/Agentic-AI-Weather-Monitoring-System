import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Config:
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
    WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY", "").strip()
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
    
    # Primary & Secondary Weather Telemetry Endpoints
    OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    OPEN_METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
    
    # Provider Data Fusion Endpoints
    NOAA_GFS_API_URL = "https://api.weather.gov"
    ECMWF_DATASET_URL = "https://api.open-meteo.com/v1/ecmwf"
    OPENAQ_API_URL = "https://api.openaq.org/v2/latest"
    RAINVIEWER_RADAR_URL = "https://api.rainviewer.com/public/weather-maps.json"
    
    # Cache Time-To-Live (TTL) Settings in Seconds
    CACHE_TTL_LIVE_WEATHER = 180   # 3 minutes
    CACHE_TTL_RADAR = 300          # 5 minutes
    CACHE_TTL_AIR_QUALITY = 600    # 10 minutes
    CACHE_TTL_FORECAST = 1800      # 30 minutes
