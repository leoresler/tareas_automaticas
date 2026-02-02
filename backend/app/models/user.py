from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """
    Modelo de Usuario
    
    Representa a los usuarios del sistema que pueden:
    - Registrarse y hacer login
    - Crear y gestionar tareas
    - Crear contactos
    - Usar la IA para crear tareas
    
    Atributos:
        id: Identificador único del usuario (clave primaria)
        username: Nombre de usuario único (para login)
        email: Email único (también puede usarse para login)
        full_name: Nombre completo del usuario
        hashed_password: Contraseña encriptada con bcrypt (NUNCA se guarda en texto plano)
        is_active: Si el usuario está activo (puede hacer login)
        is_superuser: Si es administrador con privilegios especiales
        created_at: Fecha de creación del usuario (se genera automáticmente)
        updated_at: Fecha de última actualización (se actualiza automáticamente)
    """
    
    # Nombre de la tabla en MySQL
    __tablename__ = "users"
    
    # === COLUMNAS ===
    
    # ID: Clave primaria, autoincremental
    # index=True crea un índice para búsquedas más rápidas
    id = Column(Integer, primary_key=True, index=True)
    
    # Username: Único, indexado, obligatorio
    # unique=True: No puede haber dos usuarios con el mismo username
    # index=True: Búsquedas rápidas por username
    # nullable=False: Campo obligatorio
    username = Column(String(50), unique=True, index=True, nullable=False)
    
    # Email: Único, indexado, obligatorio
    email = Column(String(100), unique=True, index=True, nullable=False)
    
    # Nombre completo: Opcional
    # nullable=True: Puede ser NULL (el usuario puede no poner su nombre)
    full_name = Column(String(200), nullable=True)
    
    # Contraseña hasheada: Obligatoria
    # String(255): Bcrypt genera hashes de ~60 caracteres, pero dejamos espacio
    hashed_password = Column(String(255), nullable=False)
    
    # Flags booleanos
    # default=True: Si no se especifica, el usuario estará activo por defecto
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps (marcas de tiempo)
    # server_default=func.now(): MySQL genera la fecha automáticamente al insertar
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # onupdate=func.now(): MySQL actualiza la fecha automáticamente al modificar
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # === RELACIONES ===

    # relacion con contacto
    contacts = relationship("Contact", back_populates="user", cascade="all, delete-orphan")

    # Relación con Task
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        """
        Representación en string del usuario (para debugging)
        """
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"