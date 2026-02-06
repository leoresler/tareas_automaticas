from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Request
from starlette.responses import Response
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, LoginResponse
from app.crud import user as user_crud
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    set_access_token_cookie,
    set_refresh_token_cookie,
    delete_access_token_cookie,
    delete_refresh_token_cookie
)
from app.core.config import settings
from app.models.user import User

"""
ENDPOINTS DE AUTENTICACIÓN

Este router maneja:
- Registro de usuarios
- Login (obtener token JWT)
- Obtener información del usuario actual
"""

# Crear router
router = APIRouter()

# Rate limiter específico para auth
limiter = Limiter(key_func=get_remote_address)


# ============================================
# REGISTRO DE USUARIO
# ============================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def register_user(
    request: Request,
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario.
    
    Pasos:
        1. Verifica que el email no esté registrado
        2. Verifica que el username no esté registrado
        3. Crea el usuario (la contraseña se hashea automáticamente en CRUD)
        4. Devuelve el usuario creado
    
    Request body:
        {
            "email": "user@example.com",
            "username": "johndoe",
            "password": "SecurePass123!",
            "full_name": "John Doe"  // opcional
        }
    
    Response:
        {
            "id": 1,
            "email": "user@example.com",
            "username": "johndoe",
            "full_name": "John Doe",
            "is_active": true,
            "is_superuser": false,
            "created_at": "2026-01-22T19:00:00"
        }
    """
    # Verificar si el email ya existe
    existing_user = user_crud.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Verificar si el username ya existe
    existing_user = user_crud.get_user_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username ya está registrado"
        )
    
    # Crear el usuario
    user = user_crud.create_user(db=db, user=user_in)
    
    return user


# ============================================
# LOGIN (Obtener Token JWT)
# ============================================

@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """
    Inicia sesión y devuelve un token JWT como cookie http-only.
    
    Pasos:
        1. Verifica que el usuario existe (por username o email)
        2. Verifica que la contraseña sea correcta
        3. Verifica que el usuario esté activo
        4. Crea un token JWT con el user_id
        5. Devuelve el token como cookie http-only y los datos del usuario
    
    Request body:
        {
            "username_or_email": "johndoe",  // puede ser username o email
            "password": "SecurePass123!"
        }
    
    Response:
        {
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                ...
            }
        }
    
    El token se envía como cookie http-only (más seguro).
    """
    # Autenticar usuario (verifica username/email y password)
    user = user_crud.authenticate_user(
        db,
        username_or_email=user_credentials.username_or_email,
        password=user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear tokens JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    # Establecer cookies http-only
    set_access_token_cookie(response, access_token)
    set_refresh_token_cookie(response, refresh_token)
    
    # Devolver token_type y datos del usuario
    return LoginResponse(token_type="bearer", user=user)


# ============================================
# OBTENER USUARIO ACTUAL
# ============================================

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene los datos del usuario actualmente autenticado.
    
    Este endpoint está PROTEGIDO: requiere token JWT válido.
    
    Request:
        GET /api/v1/auth/me
        Headers:
            Authorization: Bearer <token>
    
    Response:
        {
            "id": 1,
            "email": "user@example.com",
            "username": "johndoe",
            ...
        }
    
    El frontend puede usar este endpoint para:
        - Verificar si el token es válido
        - Obtener datos actualizados del usuario
        - Verificar si el usuario sigue activo
    """
    return current_user


# ============================================
# REFRESH TOKEN
# ============================================

@router.post("/refresh", response_model=LoginResponse)
def refresh(
    response: Response,
    request: Request,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> LoginResponse:
    """
    Refresca el access token usando el refresh token.
    
    Pasos:
        1. Verifica el refresh token de la cookie
        2. Valida que el usuario exista y esté activo
        3. Crea un nuevo access token
        4. Devuelve el nuevo access token y datos del usuario
    
    Este endpoint no requiere autenticación (el refresh token está en la cookie).
    
    Response:
        {
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                ...
            }
        }
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token no encontrado"
        )
    
    # Verificar el refresh token
    payload = verify_refresh_token(refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado"
        )
    
    # Obtener user_id del token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido"
        )
    
    user_id = int(user_id_str)
    
    # Verificar que el usuario exista y esté activo
    user = user_crud.get_user_by_id(db, user_id=user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo"
        )
    
    # Crear nuevo access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    # Establecer nueva cookie http-only
    set_access_token_cookie(response, access_token)
    
    # Devolver token_type y datos del usuario
    return LoginResponse(token_type="bearer", user=user)


# ============================================
# LOGOUT
# ============================================

@router.post("/logout")
def logout(response: Response) -> dict:
    """
    Logout del usuario.
    
    Elimina las cookies http-only de access y refresh token.
    """
    delete_access_token_cookie(response)
    delete_refresh_token_cookie(response)
    return {"message": "Logout exitoso"}