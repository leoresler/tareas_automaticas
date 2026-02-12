from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.database import engine
from sqlalchemy import text

# Importar modelos
from app.models import Base, User, Contact, Task

# Importar routers
from app.api.routes import auth, users, contacts, tasks, task_history, ai, dashboard

# Importar manejadores de excepciones
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler
)

# Importar rate limiting
from app.core.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

# Crear app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    description="API para gestión de tareas automatizadas con IA"
)

# Configurar rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar manejadores de excepciones
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

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

app.include_router(
    dashboard.router,
    prefix=f"{settings.API_V1_PREFIX}/dashboard",
    tags=["Dashboard"]
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
    """Health check para Render"""
    try:
        # Test de conexión a DB
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        from datetime import datetime
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@app.get("/test-db")
def test_database():
    """Test de conexión a la base de datos"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as number"))
            row = result.fetchone()
            
            result_db = connection.execute(text("SELECT current_database() as db_name"))
            db_row = result_db.fetchone()
            
            return {
                "status": "success",
                "message": "✅ Conectado a PostgreSQL/Supabase",
                "database": db_row[0] if db_row else None
            }
    except Exception as e:
        return {
            "status": "error",
            "message": "❌ Error de conexión",
            "error": str(e)
        }