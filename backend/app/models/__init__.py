"""
Modelos de base de datos
"""
from app.database import Base
from .user import User
from .contact import Contact, ChannelType
from .task import Task, TaskStatus, task_contacts
from .task_history import TaskHistory
from .ai_request import AIRequest, InputType

# Lista de todos los modelos disponibles
__all__ = [
    "Base",
    "User",
    "Contact",
    "ChannelType",
    "Task",
    "TaskStatus",
    "task_contacts",
    "TaskHistory",
    "AIRequest",
    "InputType"
]