from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus
from app.models.contact import Contact
from app.schemas.task import TaskCreate, TaskUpdate
from typing import Optional, List
from datetime import datetime

"""
CRUD DE TAREA

Funciones para crear, leer, actualizar y eliminar tareas.
"""


# ============================================
# UTILIDADES PARA TAGS
# ============================================
def tags_list_to_string(tags: Optional[List[str]]) -> str:
    """
    Convierte una lista de tags a un string separado por comas.
    
    Args:
        tags: Lista de tags
    
    Returns:
        String con tags separados por comas
    """
    return ",".join(tags) if tags else ""


def tags_string_to_list(tags_string: str) -> List[str]:
    """
    Convierte un string de tags separados por comas a una lista.
    
    Args:
        tags_string: String con tags separados por comas
    
    Returns:
        Lista de tags
    """
    if not tags_string:
        return []
    
    # Dividir por comas y limpiar espacios
    return [tag.strip() for tag in tags_string.split(",") if tag.strip()]


# ============================================
# CREATE (Crear)
# ============================================

def create_task(
    db: Session,
    task: TaskCreate,
    user_id: int,
    contact_ids: List[int]
) -> Task:
    """
    Crea una nueva tarea y le asigna los contactos.
    
    Args:
        db: Sesión de base de datos
        task: Datos de la tarea
        user_id: ID del usuario dueño de la tarea
        contact_ids: Lista de IDs de contactos a asignar
    
    Returns:
        Tarea creada con todos sus datos
    """
    # Validar que los contactos existan y pertenezcan al usuario
    contacts = db.query(Contact).filter(
        Contact.id.in_(contact_ids),
        Contact.user_id == user_id,
        Contact.is_active == True
    ).all()
    
    if len(contacts) != len(contact_ids):
        raise ValueError("Algunos contactos no existen o no pertenecen al usuario")
    
    # Crear la tarea
    db_task = Task(
        user_id=user_id,
        title=task.title,
        description=task.description,
        scheduled_datetime=task.scheduled_datetime,
        status=TaskStatus.PENDIENTE,
        tags=tags_list_to_string(task.tags),
        is_sent=False,
        is_active=True,
        created_by_ai=False
    )
    
    db.add(db_task)
    db.flush()  # Para obtener el ID de la tarea
    
    # Asignar contactos a la tarea (many-to-many)
    db_task.contacts = contacts
    
    db.commit()
    db.refresh(db_task)
    
    return db_task


# ============================================
# READ (Leer)
# ============================================

def get_task_by_id(db: Session, task_id: int, user_id: int) -> Optional[Task]:
    """
    Obtiene una tarea por su ID.
    Solo devuelve la tarea si pertenece al usuario.
    
    Args:
        db: Sesión de base de datos
        task_id: ID de la tarea
        user_id: ID del usuario (para verificar permisos)
    
    Returns:
        Tarea si existe y pertenece al usuario, None si no
    """
    return db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()


def get_tasks_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    is_sent: Optional[bool] = None,
    tags: Optional[List[str]] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> List[Task]:
    """
    Obtiene todas las tareas de un usuario con filtros opcionales.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        skip: Registros a saltar (paginación)
        limit: Máximo de registros
        status: Filtrar por estado (opcional)
        is_sent: Filtrar por estado de envío (opcional)
        tags: Filtrar por tags (opcional)
        date_from: Fecha mínima (opcional)
        date_to: Fecha máxima (opcional)
    
    Returns:
        Lista de tareas
    """
    query = db.query(Task).filter(Task.user_id == user_id)
    
    # Aplicar filtros opcionales
    if status is not None:
        query = query.filter(Task.status == status)
    
    if is_sent is not None:
        query = query.filter(Task.is_sent == is_sent)
    
    if tags is not None:
        # Filtrar por tags (búsqueda parcial)
        for tag in tags:
            query = query.filter(Task.tags.like(f"%{tag}%"))
    
    if date_from is not None:
        query = query.filter(Task.scheduled_datetime >= date_from)
    
    if date_to is not None:
        query = query.filter(Task.scheduled_datetime <= date_to)
    
    # Ordenar por fecha programada
    query = query.order_by(Task.scheduled_datetime)
    
    return query.offset(skip).limit(limit).all()


def search_tasks(
    db: Session,
    user_id: int,
    search_term: str,
    skip: int = 0,
    limit: int = 100
) -> List[Task]:
    """
    Busca tareas por título o descripción.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        search_term: Término de búsqueda
        skip: Registros a saltar
        limit: Máximo de registros
    
    Returns:
        Lista de tareas que coinciden con la búsqueda
    """
    search_pattern = f"%{search_term}%"
    
    return db.query(Task).filter(
        Task.user_id == user_id,
        (Task.title.ilike(search_pattern) | Task.description.ilike(search_pattern))
    ).order_by(Task.scheduled_datetime).offset(skip).limit(limit).all()


def get_tasks_to_send(db: Session, before_datetime: datetime) -> List[Task]:
    """
    Obtiene tareas pendientes que deben enviarse antes de una fecha.
    
    Args:
        db: Sesión de base de datos
        before_datetime: Fecha límite para el envío
    
    Returns:
        Lista de tareas pendientes que alcanzaron su fecha programada
    """
    return db.query(Task).filter(
        Task.status == TaskStatus.PENDIENTE,
        Task.is_active == True,
        Task.is_sent == False,
        Task.scheduled_datetime <= before_datetime
    ).order_by(Task.scheduled_datetime).all()


# ============================================
# UPDATE (Actualizar)
# ============================================

def update_task(
    db: Session,
    task_id: int,
    user_id: int,
    task_update: TaskUpdate
) -> Optional[Task]:
    """
    Actualiza una tarea.
    
    Args:
        db: Sesión de base de datos
        task_id: ID de la tarea
        user_id: ID del usuario (para verificar permisos)
        task_update: Nuevos datos de la tarea
    
    Returns:
        Tarea actualizada si existe y pertenece al usuario, None si no
    """
    # Buscar la tarea
    db_task = get_task_by_id(db, task_id, user_id)
    if not db_task:
        return None
    
    # Obtener solo los campos que NO son None
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Actualizar contactos si se proporcionan
    if "contact_ids" in update_data:
        contact_ids = update_data.pop("contact_ids")
        
        # Validar que los contactos existan y pertenezcan al usuario
        contacts = db.query(Contact).filter(
            Contact.id.in_(contact_ids),
            Contact.user_id == user_id,
            Contact.is_active == True
        ).all()
        
        if len(contacts) != len(contact_ids):
            raise ValueError("Algunos contactos no existen o no pertenecen al usuario")
        
        # Reemplazar todos los contactos
        db_task.contacts = contacts
    
    # Si se actualiza status, convertir enum a string
    if "status" in update_data:
        update_data["status"] = update_data["status"].value
    
    # Si se actualizan tags, convertir lista a string
    if "tags" in update_data:
        update_data["tags"] = tags_list_to_string(update_data["tags"])
    
    # Actualizar cada campo
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    
    return db_task


def change_task_status(
    db: Session,
    task_id: int,
    user_id: int,
    new_status: TaskStatus
) -> Optional[Task]:
    """
    Cambia el estado de una tarea.
    
    Args:
        db: Sesión de base de datos
        task_id: ID de la tarea
        user_id: ID del usuario (para verificar permisos)
        new_status: Nuevo estado de la tarea
    
    Returns:
        Tarea actualizada si existe y pertenece al usuario, None si no
    """
    db_task = get_task_by_id(db, task_id, user_id)
    if not db_task:
        return None
    
    db_task.status = new_status
    db.commit()
    db.refresh(db_task)
    
    return db_task


# ============================================
# DELETE (Eliminar)
# ============================================

def delete_task(db: Session, task_id: int, user_id: int) -> bool:
    """
    Elimina una tarea (soft delete - la cancela).
    
    Args:
        db: Sesión de base de datos
        task_id: ID de la tarea
        user_id: ID del usuario (para verificar permisos)
    
    Returns:
        True si se eliminó, False si no existe o no pertenece al usuario
    """
    db_task = get_task_by_id(db, task_id, user_id)
    if not db_task:
        return False
    
    # Soft delete: cancelar la tarea
    db_task.status = TaskStatus.CANCELADA
    db_task.is_active = False
    db.commit()
    
    return True


# ============================================
# GESTIÓN DE CONTACTOS
# ============================================

def add_contacts_to_task(
    db: Session,
    task_id: int,
    user_id: int,
    contact_ids: List[int]
) -> Optional[Task]:
    """
    Agrega contactos a una tarea existente.
    
    Args:
        db: Sesión de base de datos
        task_id: ID de la tarea
        user_id: ID del usuario (para verificar permisos)
        contact_ids: Lista de IDs de contactos a agregar
    
    Returns:
        Tarea actualizada si existe y pertenece al usuario, None si no
    """
    db_task = get_task_by_id(db, task_id, user_id)
    if not db_task:
        return None
    
    # Validar que los contactos existan y pertenezcan al usuario
    contacts = db.query(Contact).filter(
        Contact.id.in_(contact_ids),
        Contact.user_id == user_id,
        Contact.is_active == True
    ).all()
    
    if len(contacts) != len(contact_ids):
        raise ValueError("Algunos contactos no existen o no pertenecen al usuario")
    
    # Obtener contactos actuales
    current_contact_ids = {contact.id for contact in db_task.contacts}
    
    # Agregar nuevos contactos (evitar duplicados)
    for contact in contacts:
        if contact.id not in current_contact_ids:
            db_task.contacts.append(contact)
    
    db.commit()
    db.refresh(db_task)
    
    return db_task


def remove_contacts_from_task(
    db: Session,
    task_id: int,
    user_id: int,
    contact_ids: List[int]
) -> Optional[Task]:
    """
    Remueve contactos de una tarea existente.
    
    Args:
        db: Sesión de base de datos
        task_id: ID de la tarea
        user_id: ID del usuario (para verificar permisos)
        contact_ids: Lista de IDs de contactos a remover
    
    Returns:
        Tarea actualizada si existe y pertenece al usuario, None si no
    """
    db_task = get_task_by_id(db, task_id, user_id)
    if not db_task:
        return None
    
    # Crear conjunto de IDs a remover
    contact_ids_to_remove = set(contact_ids)
    
    # Filtrar contactos que NO están en la lista de eliminación
    db_task.contacts = [
        contact for contact in db_task.contacts
        if contact.id not in contact_ids_to_remove
    ]
    
    # Validar que quede al menos un contacto
    if len(db_task.contacts) < 1:
        raise ValueError("La tarea debe tener al menos un contacto")
    
    db.commit()
    db.refresh(db_task)
    
    return db_task


# ============================================
# ESTADO Y ENVÍO
# ============================================

def mark_task_as_sent(db: Session, task_id: int) -> Optional[Task]:
    """
    Marca una tarea como enviada.
    
    Args:
        db: Sesión de base de datos
        task_id: ID de la tarea
    
    Returns:
        Tarea actualizada si existe, None si no
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        return None
    
    db_task.is_sent = True
    db_task.sent_at = datetime.utcnow()
    db_task.status = TaskStatus.ENVIADA
    
    db.commit()
    db.refresh(db_task)
    
    return db_task


# ============================================
# UTILIDADES Y ESTADÍSTICAS
# ============================================

def count_tasks_by_user(db: Session, user_id: int) -> int:
    """
    Cuenta cuántas tareas tiene un usuario (solo activas).
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
    
    Returns:
        Número de tareas
    """
    return db.query(Task).filter(
        Task.user_id == user_id,
        Task.is_active == True
    ).count()
