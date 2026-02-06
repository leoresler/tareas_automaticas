from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

# Ruta al archivo .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    """
    Configuracion central de la aplicacion.
    Lee automaticamente las variables del archivo .env
    """
    
    # ============================================
    # DATABASE
    # ============================================
    DATABASE_URL: str
    
    # ============================================
    # API
    # ============================================
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Tareas Automaticas API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # ============================================
    # SECURITY
    # ============================================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ============================================
    # CORS
    # ============================================
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        case_sensitive = True

# Instancia unica de configuracion
settings = Settings()