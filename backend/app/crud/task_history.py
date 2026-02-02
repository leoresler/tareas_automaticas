from sqlalchemy.orm import Session
from app.models.task_history import TaskHistory
from app.schemas.task_history import TaskHistoryCreate
from typing import Optional, List

"""
CRUD DE HISTORIAL DE TAREA

Funciones para crear y leer registros de historial de tareas.
"""


# ============================================
# CREATE (Crear)
# ============================================

def create_history_entry(
    db: Session,
    task_id: int,
    user_id: Optional[int],
    action: str,
    field_changed: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    notes: Optional[str] = None
) -> TaskHistory:
    """
    Crea un registro de historial para una tarea.
    
    Args:
        db: Sesión de base de datos
        task_id: ID de la tarea
        user_id: ID del usuario que realizó la acción
        action: Acción realizada (creada, modificada, etc.)
        field_changed: Campo que fue modificado
        old_value: Valor anterior
        new_value: Valor nuevo
        notes: Notas adicionales
    
    Returns:
        Registro de historial creado
    """
    history_entry = TaskHistory(
        task_id=task_id,
        user_id=user_id,
        action=action,
        field_changed=field_changed,
        old_value=old_value,
        new_value=new_value,
        notes=notes
    )
    
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)
    
    return history_entry


# ============================================
# READ (Leer)
# ============================================

def get_history_by_task(
    db: Session,
    task_id: int,
    user_id: int
) -> List[TaskHistory]:
    """
    Obtiene el historial de una tarea.
    
    Args:
        db: Sesión de base de datos
        task_id: ID de la tarea
        user_id: ID del usuario (para verificar permisos)
    
    Returns:
        Lista de registros de historial ordenados por fecha
    """
    # Verificar que la tarea pertenece al usuario
    from app.models.task import Task
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()
    
    if not task:
        return []
    
    return db.query(TaskHistory).filter(
        TaskHistory.task_id == task_id
    ).order_by(TaskHistory.created_at.desc()).all()
