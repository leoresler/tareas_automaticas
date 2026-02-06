from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request


def get_user_identifier(request: Request) -> str:
    """
    Obtiene un identificador único del usuario para rate limiting.
    
    Prioridad:
    1. User ID si está autenticado
    2. IP del cliente si no está autenticado
    
    Args:
        request: Objeto Request de FastAPI
    
    Returns:
        String identificador único del usuario
    """
    # Verificar si el usuario está autenticado
    # Esto requiere que el request tenga el usuario cargado
    if hasattr(request.state, 'user') and request.state.user:
        return f"user_{request.state.user.id}"
    
    # Usar IP del cliente como fallback
    return get_remote_address(request)


# Crear instancia del limiter
# Nota: En producción, usar Redis como backend para rate limiting distribuido
limiter = Limiter(key_func=get_user_identifier)


# Límites de rate limiting por endpoint
RATE_LIMITS = {
    # Auth endpoints - más estrictos para prevenir ataques de fuerza bruta
    "auth_login": "5/minute",
    "auth_register": "3/minute",
    "auth_refresh": "10/minute",
    "auth_logout": "20/minute",
    
    # API general - límites moderados
    "default": "60/minute",
    "strict": "30/minute",
    "loose": "120/minute",
    
    # CRUD endpoints - límites específicos
    "create_resource": "30/minute",
    "read_resource": "100/minute",
    "update_resource": "60/minute",
    "delete_resource": "30/minute",
    
    # AI endpoints - más estrictos por el costo computacional
    "ai_generate": "5/minute",
}


def get_rate_limit(endpoint_type: str = "default") -> str:
    """
    Obtiene el límite de rate para un tipo de endpoint.
    
    Args:
        endpoint_type: Tipo de endpoint (auth_login, default, etc.)
    
    Returns:
        String con el límite (ej: "60/minute")
    """
    return RATE_LIMITS.get(endpoint_type, RATE_LIMITS["default"])
