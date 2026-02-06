from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.api.deps import get_db, get_current_user
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskWithContacts,
    TaskStatusEnum,
    TaskContactsAdd,
    TaskContactsRemove,
    TaskStatusUpdate
)
from app.crud import task as task_crud
from app.crud import task_history as task_history_crud
from app.models.user import User

"""
ENDPOINTS DE TAREAS

Este router maneja:
- Crear tareas
- Listar tareas del usuario actual
- Obtener tarea por ID
- Actualizar tarea
- Eliminar tarea (cancelar)
- Gestionar contactos de tareas
- Cambiar estado de tareas
- Buscar tareas
- Estadísticas de tareas
"""

router = APIRouter()


# ============================================
# CREAR TAREA
# ============================================

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva tarea.
    
    **Validaciones automáticas:**
    
    - **Fecha programada**: Debe ser futura (no puede ser una fecha pasada)
      - Ejemplo válido: `"2026-01-25T10:00:00Z"`
      - Ejemplo inválido: `"2026-01-20T10:00:00Z"` (ya pasó)
    
    - **Título**: Entre 3 y 200 caracteres
      - Ejemplo válido: `"Enviar recordatorio de reunión"`
      - Ejemplo inválido: `"AB"` (muy corto)
    
    - **Descripción**: Máximo 2000 caracteres (opcional)
    
    - **Tags**: Máximo 10 tags, cada uno máximo 30 caracteres
      - Ejemplo válido: `["importante", "equipo", "reunión"]`
      - Ejemplo inválido: `["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]` (más de 10)
    
    - **Contactos**: Mínimo 1 contacto, deben pertenecer al usuario
    
    Request body:
```json
    {
        "title": "Enviar recordatorio de reunión",
        "description": "Recordar al equipo la reunión del lunes",
        "scheduled_datetime": "2026-01-25T10:00:00Z",
        "tags": ["importante", "equipo"],
        "contact_ids": [1, 2, 3]
    }
```
    """
    try:
        task = task_crud.create_task(
            db=db,
            task=task_in,
            user_id=current_user.id,
            contact_ids=task_in.contact_ids
        )
        
        # Crear entrada en historial
        task_history_crud.create_history_entry(
            db=db,
            task_id=task.id,
            user_id=current_user.id,
            action="creada",
            notes="Tarea creada desde la API"
        )
        
        # Preparar respuesta con tags_list y history_count
        task_dict = task.__dict__.copy()
        task_dict['tags_list'] = task.get_tags_list()
        task_dict['history_count'] = 1  # Solo la entrada de creación
        
        return TaskResponse(**task_dict)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# LISTAR TAREAS
# ============================================

@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Máximo de registros"),
    status: Optional[TaskStatusEnum] = Query(None, description="Filtrar por estado"),
    is_sent: Optional[bool] = Query(None, description="Filtrar por estado de envío"),
    tags: Optional[str] = Query(None, description="Filtrar por tags (separados por coma)"),
    date_from: Optional[date] = Query(None, description="Fecha mínima"),
    date_to: Optional[date] = Query(None, description="Fecha máxima"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todas las tareas del usuario actual.
    
    **Filtros opcionales:**
    - `status`: pendiente, en_progreso, finalizado, enviada, cancelada
    - `is_sent`: true (solo enviadas), false (no enviadas), null (todas)
    - `tags`: Filtrar por tags (ej: "importante,equipo")
    - `date_from`: Fecha mínima para scheduled_datetime
    - `date_to`: Fecha máxima para scheduled_datetime
    - `skip` y `limit`: Para paginación
    
    **Ejemplos:**
    - `/api/v1/tasks` - Todas las tareas
    - `/api/v1/tasks?status=pendiente` - Solo tareas pendientes
    - `/api/v1/tasks?is_sent=false` - Tareas no enviadas
    - `/api/v1/tasks?tags=importante` - Tareas con el tag "importante"
    - `/api/v1/tasks?date_from=2026-01-01&date_to=2026-01-31` - Tareas de enero
    - `/api/v1/tasks?skip=10&limit=20` - Página 2 (registros 11-30)
    """
    # Convertir string de tags a lista si se proporciona
    tags_list = None
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",")]
    
    # Convertir dates a datetime si se proporcionan
    dt_from = datetime.combine(date_from, datetime.min.time()) if date_from else None
    dt_to = datetime.combine(date_to, datetime.max.time()) if date_to else None
    
    tasks = task_crud.get_tasks_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status.value if status else None,
        is_sent=is_sent,
        tags=tags_list,
        date_from=dt_from,
        date_to=dt_to
    )
    
    # Agregar tags_list y history_count a cada tarea
    result = []
    for task in tasks:
        task_dict = task.__dict__.copy()
        task_dict['tags_list'] = task.get_tags_list()
        task_dict['history_count'] = len(task.history) if hasattr(task, 'history') else 0
        result.append(TaskResponse(**task_dict))
    
    return result


# ============================================
# BUSCAR TAREAS
# ============================================

@router.get("/search", response_model=List[TaskResponse])
def search_tasks(
    q: str = Query(..., min_length=1, description="Término de búsqueda"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca tareas por título o descripción.
    
    La búsqueda es insensible a mayúsculas/minúsculas y busca coincidencias parciales.
    
    **Ejemplos:**
    - `/api/v1/tasks/search?q=reunión` - Busca "reunión" en título y descripción
    - `/api/v1/tasks/search?q=recordatorio` - Busca tareas con "recordatorio"
    """
    tasks = task_crud.search_tasks(
        db=db,
        user_id=current_user.id,
        search_term=q,
        skip=skip,
        limit=limit
    )
    
    # Agregar tags_list y history_count a cada tarea
    result = []
    for task in tasks:
        task_dict = task.__dict__.copy()
        task_dict['tags_list'] = task.get_tags_list()
        task_dict['history_count'] = len(task.history) if hasattr(task, 'history') else 0
        result.append(TaskResponse(**task_dict))
    
    return result


# ============================================
# OBTENER TAREA POR ID
# ============================================

@router.get("/{task_id}", response_model=TaskWithContacts)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una tarea por su ID con sus contactos.
    
    Solo puedes ver tus propias tareas.
    """
    task = task_crud.get_task_by_id(
        db=db,
        task_id=task_id,
        user_id=current_user.id
    )
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    return task


# ============================================
# OBTENER HISTORIAL DE UNA TAREA
# ============================================

@router.get("/{task_id}/history")
def get_task_history(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el historial de cambios de una tarea.
    
    Solo el dueño puede ver el historial.
    """
    history = task_history_crud.get_history_by_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id
    )
    
    return history


# ============================================
# ACTUALIZAR TAREA
# ============================================

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza una tarea.
    
    Todos los campos son opcionales. Solo se actualizan los campos proporcionados.
    
    **IMPORTANTE:** Si actualizas `contact_ids`, se REEMPLAZAN todos los contactos
    (no se agregan a los existentes).
    
    **Ejemplo - Actualizar solo el título:**
```json
    {
        "title": "Nuevo título de la tarea"
    }
```
    
    **Ejemplo - Cambiar estado:**
```json
    {
        "status": "en_progreso"
    }
```
    """
    try:
        task = task_crud.update_task(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            task_update=task_update
        )
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        
        # Preparar respuesta con tags_list y history_count
        task_dict = task.__dict__.copy()
        task_dict['tags_list'] = task.get_tags_list()
        task_dict['history_count'] = len(task.history) if hasattr(task, 'history') else 0
        
        return TaskResponse(**task_dict)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# GESTIÓN DE CONTACTOS
# ============================================

@router.post("/{task_id}/contacts", response_model=TaskWithContacts)
def add_contacts_to_task(
    task_id: int,
    contacts_add: TaskContactsAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Agrega contactos a una tarea existente.
    
    Los contactos se agregan a los existentes (no se reemplazan).
    Los duplicados se ignoran automáticamente.
    
    **Ejemplo:**
```json
    {
        "contact_ids": [4, 5]
    }
```
    """
    try:
        task = task_crud.add_contacts_to_task(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            contact_ids=contacts_add.contact_ids
        )
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        
        # Crear entrada en historial
        task_history_crud.create_history_entry(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            action="contacto_agregado",
            new_value=f"Contactos agregados: {', '.join(str(cid) for cid in contacts_add.contact_ids)}"
        )
        
        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{task_id}/contacts", response_model=TaskWithContacts)
def remove_contacts_from_task(
    task_id: int,
    contacts_remove: TaskContactsRemove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remueve contactos de una tarea existente.
    
    La tarea debe quedar con AL MENOS un contacto después de la eliminación.
    
    **Ejemplo:**
```json
    {
        "contact_ids": [3, 5]
    }
```
    """
    try:
        task = task_crud.remove_contacts_from_task(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            contact_ids=contacts_remove.contact_ids
        )
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        
        # Crear entrada en historial
        task_history_crud.create_history_entry(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            action="contacto_eliminado",
            new_value=f"Contactos eliminados: {', '.join(str(cid) for cid in contacts_remove.contact_ids)}"
        )
        
        return task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# CAMBIAR ESTADO DE UNA TAREA
# ============================================

@router.put("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cambia el estado de una tarea.
    
    **Estados disponibles:**
    - `pendiente`: Tarea creada pero no enviada
    - `en_progreso`: Tarea siendo procesada
    - `finalizado`: Tarea completada exitosamente
    - `enviada`: Tarea enviada a los contactos
    - `cancelada`: Tarea cancelada
    
    **Ejemplo:**
```json
    {
        "status": "en_progreso"
    }
```
    """
    from app.models.task import TaskStatus
    
    try:
        task = task_crud.change_task_status(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            new_status=TaskStatus(status_update.status.value)
        )
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        
        # Crear entrada en historial
        task_history_crud.create_history_entry(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            action="estado_cambiado",
            field_changed="status",
            new_value=status_update.status.value
        )
        
        # Preparar respuesta con tags_list y history_count
        task_dict = task.__dict__.copy()
        task_dict['tags_list'] = task.get_tags_list()
        task_dict['history_count'] = len(task.history) if hasattr(task, 'history') else 0
        
        return TaskResponse(**task_dict)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================
# ELIMINAR TAREA (SOFT DELETE)
# ============================================

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una tarea (desactivación, soft delete).
    
    La tarea no se elimina de la base de datos, solo se:
    - Marca como `is_active = false`
    - Cambia el estado a `cancelada`
    
    El historial se elimina automáticamente por CASCADE.
    Puedes reactivarla después actualizando los campos.
    """
    success = task_crud.delete_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    return None


# ============================================
# ESTADÍSTICAS DE TAREAS
# ============================================

# NOTA: El endpoint /stats/summary se eliminó para evitar duplicidad.
# Use /api/v1/dashboard/stats para obtener estadísticas de tareas.
