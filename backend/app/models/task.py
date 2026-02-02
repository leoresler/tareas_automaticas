from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

"""
MODELO DE TAREA

Representa las tareas automatizadas que pueden enviarse a múltiples contactos.
Cada tarea pertenece a un usuario y puede tener múltiples contactos asociados.
"""

# ============================================
# TABLA DE ASOCIACIÓN MANY-TO-MANY
# ============================================
# Esta tabla intermedia permite que una tarea tenga múltiples contactos
# y un contacto pueda estar en múltiples tareas
task_contacts = Table(
    'task_contacts',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('contact_id', Integer, ForeignKey('contacts.id', ondelete='CASCADE'), primary_key=True)
)


# ============================================
# ENUM DE ESTADO DE TAREA
# ============================================
class TaskStatus(str, enum.Enum):
    """
    Estados posibles de una tarea.
    
    - pendiente: Tarea creada pero aún no enviada
    - en_progreso: Tarea siendo procesada/enviada
    - finalizado: Tarea completada exitosamente
    - enviada: Tarea enviada a los contactos
    - cancelada: Tarea cancelada por el usuario
    """
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    FINALIZADO = "finalizado"
    ENVIADA = "enviada"
    CANCELADA = "cancelada"


# ============================================
# MODELO DE TAREA
# ============================================
class Task(Base):
    """
    Modelo de Tarea - Tareas automatizadas para enviar a contactos.
    
    Atributos:
        id: Identificador único de la tarea
        user_id: ID del usuario dueño de la tarea
        title: Título de la tarea
        description: Descripción detallada de la tarea
        scheduled_datetime: Fecha y hora programada para envío
        status: Estado actual de la tarea (enum)
        tags: Lista de etiquetas (guardadas como string separado por comas)
        is_sent: Si la tarea ya fue enviada
        sent_at: Fecha y hora en que se envió la tarea
        is_active: Si la tarea está activa (soft delete)
        created_by_ai: Si la tarea fue creada automáticamente por IA
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    
    Relaciones:
        user: Usuario dueño de la tarea
        contacts: Contactos asociados a esta tarea (many-to-many)
    """
    
    __tablename__ = "tasks"
    
    # === COLUMNAS ===
    
    # ID: Clave primaria
    id = Column(Integer, primary_key=True, index=True)
    
    # user_id: Relación con User
    # ondelete="CASCADE": Si se elimina el usuario, se eliminan sus tareas
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Título de la tarea
    title = Column(String(200), nullable=False, index=True)
    
    # Descripción de la tarea
    description = Column(Text, nullable=True)
    
    # Fecha y hora programada para envío
    scheduled_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Estado de la tarea
    status = Column(
        SQLEnum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDIENTE,
        index=True
    )
    
    # Tags (guardados como string: "tag1,tag2,tag3")
    tags = Column(String(500), nullable=True)
    
    # Si la tarea ya fue enviada
    is_sent = Column(Boolean, default=False, nullable=False)
    
    # Fecha en que se envió la tarea
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Soft delete: si la tarea está activa
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Si fue creada por IA
    created_by_ai = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # === RELACIONES ===
    
    # Relación con User
    user = relationship("User", back_populates="tasks")
    
    # Relación con Contact (many-to-many)
    contacts = relationship(
        "Contact",
        secondary=task_contacts,
        back_populates="tasks"
    )
    
    # Relación con TaskHistory (one-to-many)
    history = relationship("TaskHistory", back_populates="task", cascade="all, delete-orphan")
    
    def get_tags_list(self) -> list[str]:
        """
        Convierte tags string a lista.
        
        Returns:
            Lista de tags o lista vacía si no hay tags
        """
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]
    
    def set_tags_list(self, tags: list[str]) -> None:
        """
        Convierte lista a tags string.
        
        Args:
            tags: Lista de tags
        """
        self.tags = ",".join(tags) if tags else None
    
    def __repr__(self):
        """Representación en string de la tarea"""
        return f"<Task(id={self.id}, title={self.title}, status={self.status.value})>"
