from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import SessionLocal
from app.core.security import decode_access_token
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.user import TokenData

"""
DEPENDENCIAS DE LA API

Las dependencias son funciones que se ejecutan ANTES de los endpoints
para preparar datos que necesitan (como la sesión de DB o el usuario autenticado).

En FastAPI usamos Depends() para inyectar estas dependencias.
"""

# ============================================
# DATABASE DEPENDENCY
# ============================================

def get_db() -> Generator:
    """
    Dependency que proporciona una sesión de base de datos.
    
    Se usa así en los endpoints:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            # Aquí 'db' ya está lista para usar
            users = db.query(User).all()
            return users
    
    Ventajas:
        - Se cierra automáticamente después de usarse
        - Maneja errores automáticamente
        - Código más limpio
    """
    db = SessionLocal()
    try:
        yield db  # Aquí se "pausa" y devuelve la sesión al endpoint
    finally:
        db.close()  # Cuando termina el endpoint, se cierra la sesión


# ============================================
# AUTHENTICATION DEPENDENCIES
# ============================================

# OAuth2PasswordBearer: Esquema de autenticación con Bearer Token
# tokenUrl: La URL donde el frontend hace login para obtener el token
bearer_scheme = HTTPBearer()

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> User:
    token = credentials.credentials
    """
    Dependency que obtiene el usuario actual desde el token JWT.
    
    Se usa para proteger endpoints que requieren autenticación:
        @app.get("/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    
    Flujo:
        1. Extrae el token del header Authorization: Bearer <token>
        2. Decodifica el token
        3. Obtiene el user_id del token
        4. Busca el usuario en la base de datos
        5. Verifica que esté activo
        6. Devuelve el usuario
    
    Si algo falla (token inválido, usuario no existe, usuario inactivo),
    lanza una excepción 401 Unauthorized.
    """
    # Excepción que se lanzará si algo falla
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
        
        # Extraer el user_id del token
        # "sub" es el estándar JWT para el "subject" (usuario)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Crear objeto TokenData para validación
        token_data = TokenData(user_id=int(user_id))
        
    except (JWTError, ValueError):
        raise credentials_exception
    
    # Buscar el usuario en la base de datos
    user = user_crud.get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    
    # Verificar que el usuario esté activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    return user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency que verifica que el usuario sea administrador/superuser.
    
    Se usa para proteger endpoints de administración:
        @app.delete("/users/{user_id}")
        def delete_user(
            user_id: int,
            current_user: User = Depends(get_current_active_superuser)
        ):
            # Solo admins pueden eliminar usuarios
            ...
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene suficientes privilegios"
        )
    return current_user