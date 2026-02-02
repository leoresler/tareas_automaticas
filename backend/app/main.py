from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import engine
from sqlalchemy import text

# Importar modelos
from app.models import Base, User, Contact, Task

# Importar routers
from app.api.routes import auth, users, contacts, tasks, task_history, ai

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

# Crear app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    description="API para gestión de tareas automatizadas con IA"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Autenticación"]
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_PREFIX}/users",
    tags=["Usuarios"]
)

app.include_router(
    contacts.router,
    prefix=f"{settings.API_V1_PREFIX}/contacts",
    tags=["Contactos"]
)

app.include_router(
    tasks.router,
    prefix=f"{settings.API_V1_PREFIX}/tasks",
    tags=["Tareas"]
)

app.include_router(
    task_history.router,
    prefix=f"{settings.API_V1_PREFIX}/tasks",
    tags=["Historial de Tareas"]
)

app.include_router(
    ai.router,
    prefix=f"{settings.API_V1_PREFIX}/ai",
    tags=["Inteligencia Artificial"]
)

# Endpoints
@app.get("/")
def root():
    """Endpoint raíz - Información básica de la API"""
    return {
        "message": "API funcionando correctamente",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check"""
    return {"status": "ok"}

@app.get("/test-db")
def test_database():
    """Test de conexión a la base de datos"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as number"))
            row = result.fetchone()
            
            result_db = connection.execute(text("SELECT DATABASE() as db_name"))
            db_row = result_db.fetchone()
            
            return {
                "status": "success",
                "message": "✅ Conectado a MySQL",
                "database": db_row[0] if db_row else None
            }
    except Exception as e:
        return {
            "status": "error",
            "message": "❌ Error de conexión",
            "error": str(e)
        }