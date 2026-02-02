from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from typing import Optional

"""
CRUD DE USUARIO

CRUD = Create, Read, Update, Delete

Estas funciones interactúan directamente con la base de datos
para crear, leer, actualizar y eliminar usuarios.
"""

# ============================================
# CREATE (Crear)
# ============================================

def create_user(db: Session, user: UserCreate) -> User:
    """
    Crea un nuevo usuario en la base de datos.
    
    Args:
        db: Sesión de base de datos
        user: Datos del usuario (viene del request body)
    
    Returns:
        Usuario creado con todos sus datos
    
    Flujo:
        1. Recibe los datos del usuario (email, username, password)
        2. Hashea la contraseña
        3. Crea el objeto User
        4. Lo guarda en la base de datos
        5. Devuelve el usuario creado
    """
    # Hashear la contraseña ANTES de guardar
    hashed_password = get_password_hash(user.password)
    
    # Crear el objeto User con todos los datos
    # **user.model_dump(): Convierte el schema Pydantic a dict y lo expande
    # exclude={"password"}: Excluye el password porque ya lo hasheamos
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    
    # Agregar a la sesión de DB
    db.add(db_user)
    
    # Guardar en la base de datos
    db.commit()
    
    # Refrescar para obtener los datos generados por la DB (id, created_at)
    db.refresh(db_user)
    
    return db_user


# ============================================
# READ (Leer)
# ============================================

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Obtiene un usuario por su ID.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
    
    Returns:
        Usuario si existe, None si no existe
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Obtiene un usuario por su email.
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
    
    Returns:
        Usuario si existe, None si no existe
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Obtiene un usuario por su username.
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_username_or_email(db: Session, username_or_email: str) -> Optional[User]:
    """
    Obtiene un usuario por username O email (útil para login).
    
    Args:
        db: Sesión de base de datos
        username_or_email: Username o email del usuario
    
    Returns:
        Usuario si existe, None si no existe
    """
    return db.query(User).filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """
    Obtiene una lista de usuarios (con paginación).
    
    Args:
        db: Sesión de base de datos
        skip: Cuántos registros saltar (para paginación)
        limit: Máximo de registros a devolver
    
    Returns:
        Lista de usuarios
    
    Ejemplo:
        # Página 1: primeros 10 usuarios
        users = get_users(db, skip=0, limit=10)
        
        # Página 2: siguientes 10 usuarios
        users = get_users(db, skip=10, limit=10)
    """
    return db.query(User).offset(skip).limit(limit).all()


# ============================================
# UPDATE (Actualizar)
# ============================================

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """
    Actualiza los datos de un usuario.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario a actualizar
        user_update: Nuevos datos del usuario
    
    Returns:
        Usuario actualizado si existe, None si no existe
    """
    # Buscar el usuario
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    # Obtener solo los campos que NO son None
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Si se actualiza la contraseña, hashearla
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    # Actualizar cada campo
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    # Guardar cambios
    db.commit()
    db.refresh(db_user)
    
    return db_user


# ============================================
# DELETE (Eliminar)
# ============================================

def delete_user(db: Session, user_id: int) -> bool:
    """
    Elimina un usuario (soft delete - solo lo desactiva).
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario a eliminar
    
    Returns:
        True si se eliminó, False si no existe
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    # Soft delete: solo desactivar
    db_user.is_active = False
    db.commit()
    
    return True


# ============================================
# AUTENTICACIÓN
# ============================================

def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """
    Autentica un usuario (verifica username/email y contraseña).
    
    Args:
        db: Sesión de base de datos
        username_or_email: Username o email
        password: Contraseña en texto plano
    
    Returns:
        Usuario si las credenciales son correctas, None si son incorrectas
    
    Flujo:
        1. Busca el usuario por username o email
        2. Verifica que el usuario exista
        3. Verifica que la contraseña sea correcta
        4. Verifica que el usuario esté activo
        5. Devuelve el usuario o None
    """
    # Buscar usuario
    user = get_user_by_username_or_email(db, username_or_email)
    if not user:
        return None
    
    # Verificar contraseña
    if not verify_password(password, user.hashed_password):
        return None
    
    # Verificar que esté activo
    if not user.is_active:
        return None
    
    return user