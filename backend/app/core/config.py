import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Base app settings
    PROJECT_NAME: str = "Real Estate Listings API"
    API_PREFIX: str = "/api"
    PORT: int = 5001
    RELOAD: bool = True
    
    # Database settings
    DB_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data/database.db')
    CACHE_EXPIRATION: int = 5 * 24 * 60 * 60  # 5 days in seconds
    
    # API keys (from environment variables)
    RESO_SERVER_TOKEN: str = os.getenv("RESO_SERVER_TOKEN", "")
    GEOAPIFY_API_KEY: str = os.getenv("GEOAPIFY_API_KEY", "")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # Directory paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    LOGS_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "logs/backend")
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])  # Allow all origins in development
    
    # External API configuration
    RESO_BASE_URL: str = "https://api.bridgedataoutput.com/api/v2/OData/"
    GEOAPIFY_BASE_URL: str = "https://api.geoapify.com/v1/geocode/search"
    PLACES_API_BASE_URL: str = "https://places.googleapis.com/v1/places:searchNearby"
    PLACE_PHOTO_API_URL: str = "https://maps.googleapis.com/maps/api/place/photo"
    PLACE_PHOTO_API_URL_NEW: str = "https://places.googleapis.com/v1/photos:getMedia"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a global settings instance
settings = Settings() 