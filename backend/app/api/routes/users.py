from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user, get_current_active_superuser
from app.schemas.user import UserResponse, UserUpdate
from app.crud import user as user_crud
from app.models.user import User

"""
ENDPOINTS DE GESTIÓN DE USUARIOS

Este router maneja:
- Listar usuarios (solo admins)
- Obtener usuario por ID
- Actualizar usuario
- Eliminar usuario (soft delete)
"""

router = APIRouter()


# ============================================
# LISTAR USUARIOS
# ============================================

@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)  # Solo admins
):
    """
    Lista todos los usuarios (solo administradores).
    
    Query params:
        - skip: Registros a saltar (paginación)
        - limit: Máximo de registros
    
    Ejemplo:
        GET /api/v1/users?skip=0&limit=10
    """
    users = user_crud.get_users(db, skip=skip, limit=limit)
    return users


# ============================================
# OBTENER USUARIO POR ID
# ============================================

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un usuario por su ID.
    
    Restricción: Solo puedes ver tu propio perfil, excepto si eres admin.
    """
    # Verificar permisos
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este usuario"
        )
    
    user = user_crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


# ============================================
# ACTUALIZAR USUARIO
# ============================================

@router.put("/me", response_model=UserResponse)
def update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza los datos del usuario actual.
    
    Request body (todos opcionales):
        {
            "email": "newemail@example.com",
            "username": "newusername",
            "full_name": "New Name",
            "password": "NewPassword123!"
        }
    """
    # Verificar si el nuevo email ya existe (si se está cambiando)
    if user_update.email and user_update.email != current_user.email:
        existing_user = user_crud.get_user_by_email(db, email=user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
    
    # Verificar si el nuevo username ya existe (si se está cambiando)
    if user_update.username and user_update.username != current_user.username:
        existing_user = user_crud.get_user_by_username(db, username=user_update.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username ya está registrado"
            )
    
    # Actualizar usuario
    updated_user = user_crud.update_user(db, user_id=current_user.id, user_update=user_update)
    
    return updated_user


# ============================================
# ELIMINAR USUARIO
# ============================================

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)  # Solo admins
):
    """
    Elimina (desactiva) un usuario (solo administradores).
    
    NOTA: Es un soft delete, solo marca is_active=False
    """
    success = user_crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return {"message": "Usuario eliminado exitosamente"}