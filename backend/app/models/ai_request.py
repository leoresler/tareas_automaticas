from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

"""
MODELO DE SOLICITUD IA

Registra las solicitudes de interpretación hechas por el usuario
ya sea mediante texto o audio, y almacena la respuesta de la IA.
"""

# ============================================
# ENUM DE TIPO DE INPUT
# ============================================
class InputType(str, enum.Enum):
    """
    Tipos de input aceptados para la IA.
    
    - text: Texto plano ingresado por el usuario
    - audio: Transcripción de audio (previamente procesada)
    """
    TEXT = "text"
    AUDIO = "audio"


# ============================================
# MODELO DE SOLICITUD IA
# ============================================
class AIRequest(Base):
    """
    Modelo de AIRequest - Solicitudes de interpretación con IA.
    
    Atributos:
        id: Identificador único de la solicitud
        user_id: ID del usuario que hizo la solicitud
        input_text: Texto o transcripción de audio proporcionado
        input_type: Tipo de input (text o audio)
        ai_response: Respuesta completa generada por la IA
        interpreted_data: Datos extraídos (en formato JSON)
        was_confirmed: Si el usuario confirmó la interpretación
        tasks_created: IDs de tareas creadas (ej: "1,2,3")
        created_at: Fecha en que se hizo la solicitud
    
    Relaciones:
        user: Usuario que hizo la solicitud (solo para consulta)
    """
    
    __tablename__ = "ai_requests"
    
    # === COLUMNAS ===
    
    # ID: Clave primaria
    id = Column(Integer, primary_key=True, index=True)
    
    # user_id: Relación con User
    # ondelete="CASCADE": Si se elimina el usuario, se eliminan sus solicitudes
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Texto o transcripción de audio
    input_text = Column(Text, nullable=False)
    
    # Tipo de input
    input_type = Column(
        SQLEnum(InputType),
        nullable=False
    )
    
    # Respuesta completa de la IA
    ai_response = Column(Text, nullable=True)
    
    # Datos interpretados (en formato JSON)
    interpreted_data = Column(Text, nullable=True)
    
    # Si el usuario confirmó la interpretación
    was_confirmed = Column(Boolean, default=False, nullable=False)
    
    # IDs de tareas creadas (formato: "1,2,3")
    tasks_created = Column(String(500), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # === RELACIONES ===
    
    # Relación con User (solo para consulta, sin back_populates)
    user = relationship("User")
    
    def __repr__(self):
        """Representación en string de la solicitud"""
        return f"<AIRequest(id={self.id}, user_id={self.user_id}, input_type={self.input_type.value})>"
