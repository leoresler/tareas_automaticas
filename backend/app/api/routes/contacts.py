from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_current_user
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse, ChannelTypeEnum
from app.crud import contact as contact_crud
from app.models.user import User

"""
ENDPOINTS DE CONTACTOS

Este router maneja:
- Crear contactos
- Listar contactos del usuario actual
- Obtener contacto por ID
- Actualizar contacto
- Eliminar contacto
- Buscar contactos
"""

router = APIRouter()


# ============================================
# CREAR CONTACTO
# ============================================

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact_in: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo contacto.
    
    **Validaciones automáticas según el tipo de canal:**
    
    - **WhatsApp**: Debe ser un número internacional que empiece con +
      - Ejemplo válido: `+5491123456789`
      - Ejemplo inválido: `1123456789` (falta el +)
    
    - **Email**: Debe tener formato válido de email
      - Ejemplo válido: `contacto@empresa.com`
      - Ejemplo inválido: `contacto@empresa` (falta dominio)
    
    - **Telegram**: Debe empezar con @ y tener al menos 5 caracteres
      - Ejemplo válido: `@username`
      - Ejemplo inválido: `username` (falta @)
    
    Request body:
```json
    {
        "name": "Javier Pérez",
        "channel_type": "whatsapp",
        "channel_value": "+5491123456789",
        "notes": "Contacto de emergencia"
    }
```
    """
    # Crear el contacto asociado al usuario actual
    contact = contact_crud.create_contact(
        db=db,
        contact=contact_in,
        user_id=current_user.id
    )
    
    return contact


# ============================================
# LISTAR CONTACTOS
# ============================================

@router.get("/", response_model=List[ContactResponse])
def list_contacts(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Máximo de registros"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    channel_type: Optional[ChannelTypeEnum] = Query(None, description="Filtrar por tipo de canal"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos los contactos del usuario actual.
    
    **Filtros opcionales:**
    - `is_active`: true (solo activos), false (solo inactivos), null (todos)
    - `channel_type`: whatsapp, email, telegram
    - `skip` y `limit`: Para paginación
    
    **Ejemplos:**
    - `/api/v1/contacts` - Todos los contactos
    - `/api/v1/contacts?is_active=true` - Solo contactos activos
    - `/api/v1/contacts?channel_type=whatsapp` - Solo contactos de WhatsApp
    - `/api/v1/contacts?skip=10&limit=20` - Página 2 (registros 11-30)
    """
    contacts = contact_crud.get_contacts_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_active=is_active,
        channel_type=channel_type.value if channel_type else None
    )
    
    return contacts


# ============================================
# BUSCAR CONTACTOS
# ============================================

@router.get("/search", response_model=List[ContactResponse])
def search_contacts(
    q: str = Query(..., min_length=1, description="Término de búsqueda"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca contactos por nombre o valor de canal.
    
    La búsqueda es insensible a mayúsculas/minúsculas y busca coincidencias parciales.
    
    **Ejemplos:**
    - `/api/v1/contacts/search?q=javier` - Busca "javier" en nombre y canal
    - `/api/v1/contacts/search?q=@user` - Busca usuarios de Telegram
    - `/api/v1/contacts/search?q=+549` - Busca números de Argentina
    """
    contacts = contact_crud.search_contacts(
        db=db,
        user_id=current_user.id,
        search_term=q,
        skip=skip,
        limit=limit
    )
    
    return contacts


# ============================================
# OBTENER CONTACTO POR ID
# ============================================

@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene un contacto por su ID.
    
    Solo puedes ver tus propios contactos.
    """
    contact = contact_crud.get_contact_by_id(
        db=db,
        contact_id=contact_id,
        user_id=current_user.id
    )
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacto no encontrado"
        )
    
    return contact


# ============================================
# ACTUALIZAR CONTACTO
# ============================================

@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un contacto.
    
    Todos los campos son opcionales. Solo se actualizan los campos proporcionados.
    
    **Ejemplo - Actualizar solo el nombre:**
```json
    {
        "name": "Javier Pérez García"
    }
```
    
    **Ejemplo - Cambiar canal de WhatsApp a Email:**
```json
    {
        "channel_type": "email",
        "channel_value": "javier@empresa.com"
    }
```
    
    **IMPORTANTE:** Si cambias `channel_type`, también debes cambiar `channel_value`
    para que coincida con el formato del nuevo canal.
    """
    contact = contact_crud.update_contact(
        db=db,
        contact_id=contact_id,
        user_id=current_user.id,
        contact_update=contact_update
    )
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacto no encontrado"
        )
    
    return contact


# ============================================
# ELIMINAR CONTACTO (SOFT DELETE)
# ============================================

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un contacto (desactivación, soft delete).
    
    El contacto no se elimina de la base de datos, solo se marca como inactivo.
    Puedes reactivarlo después actualizando `is_active` a `true`.
    """
    success = contact_crud.delete_contact(
        db=db,
        contact_id=contact_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacto no encontrado"
        )
    
    return None


# ============================================
# ELIMINAR CONTACTO PERMANENTEMENTE
# ============================================

@router.delete("/{contact_id}/permanent", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un contacto PERMANENTEMENTE de la base de datos.
    
    **⚠️ ADVERTENCIA:** Esta acción NO se puede deshacer.
    El contacto será eliminado completamente y no podrá recuperarse.
    
    Se recomienda usar el endpoint DELETE normal (soft delete) en su lugar.
    """
    success = contact_crud.hard_delete_contact(
        db=db,
        contact_id=contact_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacto no encontrado"
        )
    
    return None


# ============================================
# ESTADÍSTICAS DE CONTACTOS
# ============================================

@router.get("/stats/count")
def get_contacts_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene estadísticas de contactos del usuario.
    
    Devuelve:
    - Total de contactos activos
    - Contactos por canal (whatsapp, email, telegram)
    """
    # Total de contactos activos
    total = contact_crud.count_contacts_by_user(db, current_user.id)
    
    # Contactos por canal
    all_contacts = contact_crud.get_contacts_by_user(
        db=db,
        user_id=current_user.id,
        is_active=True,
        limit=1000
    )
    
    by_channel = {
        "whatsapp": 0,
        "email": 0,
        "telegram": 0
    }
    
    for contact in all_contacts:
        by_channel[contact.channel_type] += 1
    
    return {
        "total_contacts": total,
        "by_channel": by_channel
    }