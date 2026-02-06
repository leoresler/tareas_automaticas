from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings

"""
MÓDULO DE SEGURIDAD

Este módulo maneja:
1. Hash de contraseñas con bcrypt
2. Creación de tokens JWT
3. Verificación de tokens JWT
"""

# ============================================
# CONFIGURACIÓN DE BCRYPT
# ============================================
# CryptContext: Maneja el hasheo de contraseñas
# schemes=["bcrypt"]: Usa el algoritmo bcrypt
# deprecated="auto": Marca como obsoletos algoritmos antiguos automáticamente
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================
# FUNCIONES DE CONTRASEÑAS
# ============================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con el hash.
    
    Args:
        plain_password: Contraseña ingresada por el usuario (ej: "mipass123")
        hashed_password: Hash almacenado en la base de datos
    
    Returns:
        True si coinciden, False si no
    
    Ejemplo:
        stored_hash = "$2b$12$..."  # hash de la DB
        if verify_password("mipass123", stored_hash):
            print("Contraseña correcta!")
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera un hash bcrypt de la contraseña.
    
    Args:
        password: Contraseña en texto plano
    
    Returns:
        Hash de la contraseña (string de ~60 caracteres)
    
    Ejemplo:
        hash = get_password_hash("mipass123")
        # hash = "$2b$12$abcd1234..."
        # Este hash es lo que se guarda en la base de datos
    """
    return pwd_context.hash(password)


# ============================================
# FUNCIONES DE JWT TOKENS
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT token de acceso.
    
    Args:
        data: Datos a incluir en el token (ej: {"sub": "1", "username": "john"})
        expires_delta: Tiempo de expiración personalizado (opcional)
    
    Returns:
        Token JWT como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT token de refresh.
    
    Args:
        data: Datos a incluir en el token (ej: {"sub": "1", "username": "john"})
        expires_delta: Tiempo de expiración personalizado (opcional)
    
    Returns:
        Token JWT de refresh como string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_refresh_token(token: str) -> Optional[dict]:
    """
    Verifica y decodifica un refresh token.
    
    Args:
        token: Token JWT de refresh a verificar
    
    Returns:
        Datos del token si es válido y es de tipo refresh, None si no
    """
    payload = decode_access_token(token)
    
    if payload and payload.get("type") == "refresh":
        return payload
    
    return None
    """
    Crea un JWT token.
    
    Args:
        data: Datos a incluir en el token (ej: {"sub": "1", "username": "john"})
        expires_delta: Tiempo de expiración personalizado (opcional)
    
    Returns:
        Token JWT como string
    
    Cómo funciona:
        1. Toma los datos que le pasas
        2. Les agrega una fecha de expiración
        3. Los firma con SECRET_KEY
        4. Devuelve un string encriptado
    
    Ejemplo:
        token = create_access_token({"sub": "1", "username": "john"})
        # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    # Copia los datos para no modificar el original
    to_encode = data.copy()
    
    # Calcula cuándo expira el token
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Agrega la fecha de expiración a los datos
    to_encode.update({"exp": expire})
    
    # Crea el token firmado con SECRET_KEY
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un JWT token.
    
    Args:
        token: Token JWT a decodificar
    
    Returns:
        Datos del token si es válido, None si es inválido o expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# ============================================
# FUNCIONES DE COOKIES
# ============================================

def set_access_token_cookie(response, token: str):
    """
    Establece el token JWT de acceso como una cookie http-only.
    
    Args:
        response: Objeto Response de FastAPI
        token: Token JWT a guardar en la cookie
    
    Returns:
        Response con la cookie configurada
    """
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="strict",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response


def set_refresh_token_cookie(response, token: str):
    """
    Establece el token JWT de refresh como una cookie http-only.
    
    Args:
        response: Objeto Response de FastAPI
        token: Token JWT de refresh a guardar en la cookie
    
    Returns:
        Response con la cookie configurada
    """
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    return response


def delete_access_token_cookie(response):
    """
    Elimina la cookie de acceso.
    
    Args:
        response: Objeto Response de FastAPI
    
    Returns:
        Response con la cookie eliminada
    """
    response.delete_cookie(key="access_token", path="/", domain=None)
    return response


def delete_refresh_token_cookie(response):
    """
    Elimina la cookie de refresh.
    
    Args:
        response: Objeto Response de FastAPI
    
    Returns:
        Response con la cookie eliminada
    """
    response.delete_cookie(key="refresh_token", path="/", domain=None)
    return response