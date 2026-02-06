from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.crud import dashboard as dashboard_crud

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene estadísticas generales del dashboard.
    """
    try:
        stats = dashboard_crud.get_dashboard_stats(db, current_user.id)
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get("/tasks-by-status")
def get_tasks_by_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene distribución de tareas por estado para gráficos.
    """
    try:
        data = dashboard_crud.get_tasks_by_status(db, current_user.id)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tareas por estado: {str(e)}"
        )


@router.get("/tasks-by-month")
def get_tasks_by_month(
    months: int = Query(default=6, ge=1, le=12, description="Número de meses a consultar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtendistribución de tareas por mes para gráficos de tendencia.
    """
    try:
        data = dashboard_crud.get_tasks_by_month(db, current_user.id, months)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tareas por mes: {str(e)}"
        )


@router.get("/recent-tasks")
def get_recent_tasks(
    limit: int = Query(default=10, ge=1, le=50, description="Número máximo de tareas"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene tareas recientes para el dashboard.
    """
    try:
        data = dashboard_crud.get_recent_tasks(db, current_user.id, limit)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tareas recientes: {str(e)}"
        )


@router.get("/today-tasks")
def get_today_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene tareas programadas para hoy.
    """
    try:
        data = dashboard_crud.get_today_tasks(db, current_user.id)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tareas de hoy: {str(e)}"
        )