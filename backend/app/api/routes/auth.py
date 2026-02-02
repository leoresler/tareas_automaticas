from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import Response
from sqlalchemy.orm import Session
from datetime import timedelta

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, LoginResponse
from app.crud import user as user_crud
from app.core.security import create_access_token, set_access_token_cookie, delete_access_token_cookie
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


# ============================================
# REGISTRO DE USUARIO
# ============================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
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
def login(
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
    
    # Crear token JWT
    # "sub" (subject) es el estándar para identificar al usuario
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    # Establecer cookie http-only
    set_access_token_cookie(response, access_token)
    
    # Devolver token_type y datos del usuario
    return {
        "token_type": "bearer",
        "user": user
    }


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
# LOGOUT (Opcional - lado del frontend)
# ============================================

@router.post("/logout")
def logout(response: Response) -> dict:
    """
    Logout del usuario.
    
    Elimina la cookie http-only del token.
    """
    delete_access_token_cookie(response)
    return {"message": "Logout exitoso"}