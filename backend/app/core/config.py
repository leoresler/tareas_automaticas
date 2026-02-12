from pydantic_settings import BaseSettings
from typing import List, Optional
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
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def DATABASE_URL_ASYNC(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
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
    # FIRST SUPERUSER
    # ============================================
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str
    
    # ============================================
    # CORS
    # ============================================
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "ignore"

# Instancia unica de configuracion
settings = Settings()