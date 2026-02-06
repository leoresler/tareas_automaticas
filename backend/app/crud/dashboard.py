from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import Task, Contact
from app.schemas import TaskStatusEnum


def get_dashboard_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Obtiene estadísticas generales del dashboard para un usuario.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Diccionario con estadísticas generales
    """
    total_tasks = db.query(Task).filter(Task.user_id == user_id).count()
    
    # Tareas por estado
    pending_count = db.query(Task).filter(
        Task.user_id == user_id,
        Task.status == TaskStatusEnum.PENDIENTE
    ).count()
    
    in_progress_count = db.query(Task).filter(
        Task.user_id == user_id,
        Task.status == TaskStatusEnum.EN_PROGRESO
    ).count()
    
    completed_count = db.query(Task).filter(
        Task.user_id == user_id,
        Task.status == TaskStatusEnum.FINALIZADO
    ).count()
    
    # Tareas de hoy
    today = datetime.now().date()
    today_tasks = db.query(Task).filter(
        Task.user_id == user_id,
        func.date(Task.scheduled_datetime) == today
    ).count()
    
    # Tareas vencidas
    overdue_count = db.query(Task).filter(
        Task.user_id == user_id,
        Task.scheduled_datetime < datetime.now(),
        Task.status.in_([TaskStatusEnum.PENDIENTE, TaskStatusEnum.EN_PROGRESO])
    ).count()
    
    # Tareas completadas esta semana
    week_start = today - timedelta(days=today.weekday())
    week_completed = db.query(Task).filter(
        Task.user_id == user_id,
        Task.status == TaskStatusEnum.FINALIZADO,
        func.date(Task.completed_at) >= week_start
    ).count()
    
    return {
        "total_tasks": total_tasks,
        "pending_count": pending_count,
        "in_progress_count": in_progress_count,
        "completed_count": completed_count,
        "today_tasks": today_tasks,
        "overdue_count": overdue_count,
        "week_completed": week_completed,
        "completion_rate": round((completed_count / total_tasks * 100) if total_tasks > 0 else 0, 1)
    }


def get_tasks_by_status(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Obtiene distribución de tareas por estado para gráficos.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Lista con conteos por estado
    """
    result = db.query(
        Task.status,
        func.count(Task.id).label('count')
    ).filter(
        Task.user_id == user_id
    ).group_by(Task.status).all()
    
    status_map = {
        TaskStatusEnum.PENDIENTE: "Pendiente",
        TaskStatusEnum.EN_PROGRESO: "En Progreso", 
        TaskStatusEnum.FINALIZADO: "Finalizado"
    }
    
    return [
        {
            "status": status_map.get(status, str(status)),
            "count": count,
            "color": _get_status_color(status)
        }
        for status, count in result
    ]


def get_tasks_by_month(db: Session, user_id: int, months: int = 6) -> List[Dict[str, Any]]:
    """
    Obtiene distribución de tareas por mes para gráficos de tendencia.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        months: Número de meses a retroceder
        
    Returns:
        Lista con conteos por mes
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    result = db.query(
        extract('year', Task.created_at).label('year'),
        extract('month', Task.created_at).label('month'),
        func.count(Task.id).label('count')
    ).filter(
        Task.user_id == user_id,
        Task.created_at >= start_date
    ).group_by(
        extract('year', Task.created_at),
        extract('month', Task.created_at)
    ).order_by(
        extract('year', Task.created_at),
        extract('month', Task.created_at)
    ).all()
    
    month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", 
                   "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    
    return [
        {
            "month": f"{int(month)} {month_names[int(month)-1]}",
            "count": count
        }
        for year, month, count in result
    ]


def get_recent_tasks(db: Session, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Obtiene tareas recientes para mostrar en el dashboard.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        limit: Número máximo de tareas a devolver
        
    Returns:
        Lista de tareas recientes
    """
    tasks = db.query(Task).filter(
        Task.user_id == user_id
    ).order_by(
        Task.created_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": task.id,
            "title": task.title,
            "status": task.status.value,
            "scheduled_datetime": task.scheduled_datetime.isoformat() if task.scheduled_datetime else None,
            "created_at": task.created_at.isoformat(),
            "is_overdue": task.scheduled_datetime and task.scheduled_datetime < datetime.now()
                         and task.status not in [TaskStatusEnum.FINALIZADO]
        }
        for task in tasks
    ]


def get_today_tasks(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    Obtiene tareas programadas para hoy.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Lista de tareas de hoy
    """
    today = datetime.now().date()
    
    tasks = db.query(Task).filter(
        Task.user_id == user_id,
        func.date(Task.scheduled_datetime) == today
    ).order_by(Task.scheduled_datetime).all()
    
    return [
        {
            "id": task.id,
            "title": task.title,
            "status": task.status.value,
            "scheduled_datetime": task.scheduled_datetime.isoformat() if task.scheduled_datetime else None,
            "is_overdue": task.scheduled_datetime and task.scheduled_datetime < datetime.now()
                         and task.status not in [TaskStatusEnum.FINALIZADO]
        }
        for task in tasks
    ]


def _get_status_color(status: TaskStatusEnum) -> str:
    """
    Obtiene el color asociado a un estado para gráficos.
    
    Args:
        status: Estado de la tarea
        
    Returns:
        Código de color hexadecimal
    """
    colors = {
        TaskStatusEnum.PENDIENTE: "#6B7280",      # gray-500
        TaskStatusEnum.EN_PROGRESO: "#3B82F6",   # blue-500
        TaskStatusEnum.FINALIZADO: "#10B981"     # green-500
    }
    return colors.get(status, "#9CA3AF")  # gray-400 default