from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(
        extra='ignore',  # Ignore extra fields để tránh lỗi validation
        env_file='.env'  # Load từ .env file
    )
    
    # App settings
    app_name: str = "AI Companion"
    debug: bool = True
    
    # Security
    secret_key: str = "ai-companion-secret-key-2024"
    
    # Google Cloud Speech API
    google_credentials_path: Optional[str] = None
    google_project_id: Optional[str] = "ai-companion"
    google_application_credentials: Optional[str] = None  # For environment variable
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    # Audio settings
    sample_rate: int = 16000
    chunk_size: int = 1024
    
    # YAMNet model settings
    yamnet_model_url: str = "https://tfhub.dev/google/yamnet/1"
    
    # Language settings
    default_language: str = "vi-VN"  # Vietnamese
    supported_languages: list = ["vi-VN", "en-US"]

settings = Settings() 