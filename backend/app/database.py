from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Crear el engine de conexión a MySQL
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Muestra SQL en consola si DEBUG=True
    pool_pre_ping=True,   # Verifica conexión antes de usar
    pool_recycle=3600     # Recicla conexiones cada hora
)

# Crear SessionLocal para manejar sesiones de base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos
Base = declarative_base()

# Dependency para obtener sesión de DB
def get_db():
    """
    Genera una sesión de base de datos.
    Se cierra automáticamente después de usarse.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()