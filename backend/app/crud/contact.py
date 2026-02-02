from sqlalchemy.orm import Session
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate
from typing import Optional, List

"""
CRUD DE CONTACTO

Funciones para crear, leer, actualizar y eliminar contactos.
"""

# ============================================
# CREATE (Crear)
# ============================================

def create_contact(db: Session, contact: ContactCreate, user_id: int) -> Contact:
    """
    Crea un nuevo contacto.
    
    Args:
        db: Sesión de base de datos
        contact: Datos del contacto
        user_id: ID del usuario dueño del contacto
    
    Returns:
        Contacto creado
    """
    db_contact = Contact(
        user_id=user_id,
        name=contact.name,
        channel_type=contact.channel_type.value,  # Convertir enum a string
        channel_value=contact.channel_value,
        notes=contact.notes,
        is_active=True
    )
    
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    
    return db_contact


# ============================================
# READ (Leer)
# ============================================

def get_contact_by_id(db: Session, contact_id: int, user_id: int) -> Optional[Contact]:
    """
    Obtiene un contacto por su ID.
    Solo devuelve el contacto si pertenece al usuario.
    
    Args:
        db: Sesión de base de datos
        contact_id: ID del contacto
        user_id: ID del usuario (para verificar permisos)
    
    Returns:
        Contacto si existe y pertenece al usuario, None si no
    """
    return db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == user_id
    ).first()


def get_contacts_by_user(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    is_active: Optional[bool] = None,
    channel_type: Optional[str] = None
) -> List[Contact]:
    """
    Obtiene todos los contactos de un usuario con filtros opcionales.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        skip: Registros a saltar (paginación)
        limit: Máximo de registros
        is_active: Filtrar por estado activo/inactivo (opcional)
        channel_type: Filtrar por tipo de canal (opcional)
    
    Returns:
        Lista de contactos
    """
    query = db.query(Contact).filter(Contact.user_id == user_id)
    
    # Aplicar filtros opcionales
    if is_active is not None:
        query = query.filter(Contact.is_active == is_active)
    
    if channel_type is not None:
        query = query.filter(Contact.channel_type == channel_type)
    
    # Ordenar por nombre
    query = query.order_by(Contact.name)
    
    return query.offset(skip).limit(limit).all()


def search_contacts(
    db: Session, 
    user_id: int, 
    search_term: str,
    skip: int = 0,
    limit: int = 100
) -> List[Contact]:
    """
    Busca contactos por nombre o valor de canal.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        search_term: Término de búsqueda
        skip: Registros a saltar
        limit: Máximo de registros
    
    Returns:
        Lista de contactos que coinciden con la búsqueda
    """
    search_pattern = f"%{search_term}%"
    
    return db.query(Contact).filter(
        Contact.user_id == user_id,
        (Contact.name.ilike(search_pattern) | Contact.channel_value.ilike(search_pattern))
    ).order_by(Contact.name).offset(skip).limit(limit).all()


# ============================================
# UPDATE (Actualizar)
# ============================================

def update_contact(
    db: Session, 
    contact_id: int, 
    user_id: int, 
    contact_update: ContactUpdate
) -> Optional[Contact]:
    """
    Actualiza un contacto.
    
    Args:
        db: Sesión de base de datos
        contact_id: ID del contacto
        user_id: ID del usuario (para verificar permisos)
        contact_update: Nuevos datos del contacto
    
    Returns:
        Contacto actualizado si existe y pertenece al usuario, None si no
    """
    # Buscar el contacto
    db_contact = get_contact_by_id(db, contact_id, user_id)
    if not db_contact:
        return None
    
    # Obtener solo los campos que NO son None
    update_data = contact_update.model_dump(exclude_unset=True)
    
    # Si se actualiza channel_type, convertir enum a string
    if "channel_type" in update_data:
        update_data["channel_type"] = update_data["channel_type"].value
    
    # Actualizar cada campo
    for field, value in update_data.items():
        setattr(db_contact, field, value)
    
    db.commit()
    db.refresh(db_contact)
    
    return db_contact


# ============================================
# DELETE (Eliminar)
# ============================================

def delete_contact(db: Session, contact_id: int, user_id: int) -> bool:
    """
    Elimina un contacto (soft delete - lo desactiva).
    
    Args:
        db: Sesión de base de datos
        contact_id: ID del contacto
        user_id: ID del usuario (para verificar permisos)
    
    Returns:
        True si se eliminó, False si no existe o no pertenece al usuario
    """
    db_contact = get_contact_by_id(db, contact_id, user_id)
    if not db_contact:
        return False
    
    # Soft delete: solo desactivar
    db_contact.is_active = False
    db.commit()
    
    return True


def hard_delete_contact(db: Session, contact_id: int, user_id: int) -> bool:
    """
    Elimina un contacto permanentemente de la base de datos.
    
    Args:
        db: Sesión de base de datos
        contact_id: ID del contacto
        user_id: ID del usuario (para verificar permisos)
    
    Returns:
        True si se eliminó, False si no existe o no pertenece al usuario
    """
    db_contact = get_contact_by_id(db, contact_id, user_id)
    if not db_contact:
        return False
    
    # Hard delete: eliminar de la base de datos
    db.delete(db_contact)
    db.commit()
    
    return True


# ============================================
# UTILIDADES
# ============================================

def count_contacts_by_user(db: Session, user_id: int) -> int:
    """
    Cuenta cuántos contactos tiene un usuario.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
    
    Returns:
        Número de contactos
    """
    return db.query(Contact).filter(
        Contact.user_id == user_id,
        Contact.is_active == True
    ).count()