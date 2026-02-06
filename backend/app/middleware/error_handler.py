from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Manejador global para excepciones HTTP.
    
    Estandariza el formato de respuesta para todas las excepciones HTTP.
    """
    detail = exc.detail
    
    if isinstance(detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=detail
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(detail),
            "details": None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manejador para errores de validación de Pydantic.
    
    Convierte los errores de validación de Pydantic a un formato estándar.
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Error de validación",
            "details": {"errors": errors}
        }
    )


async def global_exception_handler(request: Request, exc: Exception):
    """
    Manejador global para todas las excepciones no capturadas.
    
    Registra el error y devuelve una respuesta genérica al cliente.
    """
    logger.error(f"Error no capturado: {str(exc)}", exc_info=True, extra={
        "path": request.url.path,
        "method": request.method,
        "client": request.client.host if request.client else None
    })
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Error interno del servidor",
            "details": str(exc) if settings.DEBUG else None
        }
    )
