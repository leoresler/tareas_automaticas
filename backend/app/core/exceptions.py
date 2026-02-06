from fastapi import HTTPException


class AppException(HTTPException):
    """
    Excepción base de la aplicación con formato estandarizado.
    
    Permite crear excepciones con un formato consistente de respuesta:
    - success: siempre False
    - message: mensaje de error legible para el usuario
    - details: detalles técnicos adicionales (opcional)
    
    Ejemplo:
        raise AppException(
            status_code=404,
            message="Tarea no encontrada",
            details={"task_id": 123}
        )
    
    Response:
        {
            "success": false,
            "message": "Tarea no encontrada",
            "details": {"task_id": 123}
        }
    """
    
    def __init__(
        self,
        status_code: int,
        message: str,
        details: dict | None = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "success": False,
                "message": message,
                "details": details
            }
        )


class ValidationException(AppException):
    """
    Excepción para errores de validación de datos.
    """
    
    def __init__(self, message: str, field: str | None = None, details: dict | None = None):
        error_details = {"field": field} if field else {}
        if details:
            error_details.update(details)
        
        super().__init__(
            status_code=422,
            message=message,
            details=error_details
        )


class UnauthorizedException(AppException):
    """
    Excepción para errores de autorización.
    """
    
    def __init__(self, message: str = "No autorizado", details: dict | None = None):
        super().__init__(
            status_code=401,
            message=message,
            details=details
        )


class ForbiddenException(AppException):
    """
    Excepción para errores de permisos insuficientes.
    """
    
    def __init__(self, message: str = "Permisos insuficientes", details: dict | None = None):
        super().__init__(
            status_code=403,
            message=message,
            details=details
        )


class NotFoundException(AppException):
    """
    Excepción para recursos no encontrados.
    """
    
    def __init__(self, resource: str, details: dict | None = None):
        super().__init__(
            status_code=404,
            message=f"{resource} no encontrado",
            details=details
        )


class ConflictException(AppException):
    """
    Excepción para conflictos de datos (ej: duplicados).
    """
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            status_code=409,
            message=message,
            details=details
        )
