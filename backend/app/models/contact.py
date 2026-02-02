from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

"""
MODELO DE CONTACTO

Representa a las personas que recibirán las tareas automatizadas.
Cada contacto pertenece a un usuario y tiene un canal de comunicación específico.
"""

# ============================================
# ENUM DE TIPOS DE CANAL
# ============================================
class ChannelType(str, enum.Enum):
    """
    Tipos de canales de comunicación soportados.
    
    Al usar Enum:
    - Validación automática (solo valores permitidos)
    - Fácil agregar nuevos canales (solo agregar aquí)
    - Autocompletado en IDEs
    - Documentación clara
    """
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    TELEGRAM = "telegram"
    # Fácil agregar más:
    # SMS = "sms"
    # SLACK = "slack"
    # DISCORD = "discord"


# ============================================
# MODELO DE CONTACTO
# ============================================
class Contact(Base):
    """
    Modelo de Contacto - Destinatarios de tareas.
    
    Atributos:
        id: Identificador único del contacto
        user_id: ID del usuario dueño del contacto (clave foránea)
        name: Nombre del contacto
        channel_type: Tipo de canal (whatsapp, email, telegram)
        channel_value: Valor del canal (teléfono, email, username)
        notes: Notas opcionales sobre el contacto
        is_active: Si el contacto está activo
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    
    Relaciones:
        user: Usuario dueño del contacto
        tasks: Tareas asignadas a este contacto (se agregará después)
    """
    
    __tablename__ = "contacts"
    
    # === COLUMNAS ===
    
    # ID: Clave primaria
    id = Column(Integer, primary_key=True, index=True)
    
    # user_id: Relación con User (cada contacto pertenece a un usuario)
    # ForeignKey: Crea una relación con la tabla users
    # ondelete="CASCADE": Si se elimina el usuario, se eliminan sus contactos
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Nombre del contacto
    name = Column(String(100), nullable=False, index=True)
    
    # Tipo de canal (whatsapp, email, telegram)
    # SQLEnum: Usa el enum que definimos arriba
    # MySQL lo guardará como VARCHAR pero validará los valores
    channel_type = Column(
        SQLEnum(ChannelType),
        nullable=False,
        index=True
    )
    
    # Valor del canal (teléfono, email, username)
    # Ej: "+5491123456789", "contacto@email.com", "@username"
    channel_value = Column(String(255), nullable=False)
    
    # Notas opcionales sobre el contacto
    notes = Column(Text, nullable=True)
    
    # Si el contacto está activo (soft delete)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # === RELACIONES ===
    
    # Relación con User (muchos contactos pertenecen a un usuario)
    # back_populates: Crea la relación bidireccional
    user = relationship("User", back_populates="contacts")
    
    # Relación con Task (many-to-many)
    tasks = relationship("Task", secondary="task_contacts", back_populates="contacts")
    
    def __repr__(self):
        """Representación en string del contacto"""
        return f"<Contact(id={self.id}, name={self.name}, channel={self.channel_type.value}:{self.channel_value})>"