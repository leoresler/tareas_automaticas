from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

"""
MODELO DE HISTORIAL DE TAREA

Registra todos los cambios y acciones realizadas sobre una tarea.
Esto permite mantener un registro completo del ciclo de vida de cada tarea.
"""

# ============================================
# MODELO DE HISTORIAL DE TAREA
# ============================================
class TaskHistory(Base):
    """
    Modelo de TaskHistory - Historial de cambios de tarea.
    
    Atributos:
        id: Identificador único del registro de historial
        task_id: ID de la tarea asociada
        user_id: ID del usuario que realizó la acción (puede ser NULL si se eliminó)
        action: Acción realizada (creada, modificada, enviada, etc.)
        field_changed: Campo que fue modificado
        old_value: Valor anterior (en JSON o texto)
        new_value: Valor nuevo (en JSON o texto)
        notes: Notas adicionales sobre la acción
        created_at: Fecha en que se realizó la acción
    
    Relaciones:
        task: Tarea asociada a este registro de historial
        user: Usuario que realizó la acción (solo para consulta)
    """
    
    __tablename__ = "task_history"
    
    # === COLUMNAS ===
    
    # ID: Clave primaria
    id = Column(Integer, primary_key=True, index=True)
    
    # task_id: Relación con Task
    # ondelete="CASCADE": Si se elimina la tarea, se elimina su historial
    task_id = Column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # user_id: Relación con User
    # ondelete="SET NULL": Si se elimina el usuario, se conserva el registro pero sin usuario
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Acción realizada
    # Posibles valores: "creada", "modificada", "enviada", "estado_cambiado",
    #                  "contacto_agregado", "contacto_eliminado", "cancelada"
    action = Column(String(100), nullable=False, index=True)
    
    # Campo que fue modificado
    field_changed = Column(String(100), nullable=True)
    
    # Valor anterior (en JSON o texto plano)
    old_value = Column(Text, nullable=True)
    
    # Valor nuevo (en JSON o texto plano)
    new_value = Column(Text, nullable=True)
    
    # Notas adicionales sobre la acción
    notes = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # === RELACIONES ===
    
    # Relación con Task
    task = relationship("Task", back_populates="history")
    
    # Relación con User (solo para consulta, sin back_populates)
    user = relationship("User")
    
    def __repr__(self):
        """Representación en string del historial"""
        return f"<TaskHistory(id={self.id}, task_id={self.task_id}, action={self.action})>"
