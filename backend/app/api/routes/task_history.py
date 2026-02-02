from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.schemas.task_history import TaskHistoryResponse
from app.crud import task_history as task_history_crud
from app.models.user import User
from app.models.task import Task

"""
ENDPOINTS DE HISTORIAL DE TAREAS

Este router maneja:
- Obtener historial de una tarea
"""

router = APIRouter()


# ============================================
# OBTENER HISTORIAL DE TAREA
# ============================================

@router.get("/{task_id}/history", response_model=List[TaskHistoryResponse])
def get_task_history(
    task_id: int,
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Máximo de registros"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el historial de cambios de una tarea.
    
    Solo el dueño puede ver el historial.
    
    **Ejemplo:**
    - `/api/v1/tasks/1/history` - Historial de la tarea con ID 1
    - `/api/v1/tasks/1/history?skip=10&limit=20` - Página 2
    """
    # Verificar que la tarea pertenezca al usuario
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    
    history = task_history_crud.get_history_by_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id
    )
    
    # Aplicar paginación
    return history[skip:skip + limit]
