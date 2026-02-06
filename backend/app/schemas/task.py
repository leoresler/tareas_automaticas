from pydantic import BaseModel, Field, field_validator, ConfigDict, field_serializer
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum
from app.schemas.contact import ContactResponse

"""
SCHEMAS DE TAREA

Definen cómo se validan los datos de tareas que entran y salen de la API.
"""

# ============================================
# ENUM DE ESTADO DE TAREA (para Pydantic)
# ============================================
class TaskStatusEnum(str, Enum):
    """
    Enum para validación de estados de tarea en Pydantic.
    Debe coincidir con el TaskStatus de SQLAlchemy.
    """
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    FINALIZADO = "finalizado"
    ENVIADA = "enviada"
    CANCELADA = "cancelada"


# ============================================
# SCHEMA BASE (campos comunes)
# ============================================
class TaskBase(BaseModel):
    """
    Schema base con campos comunes de tarea.
    """
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Título de la tarea",
        examples=["Enviar recordatorio de reunión", "Promoción de producto"]
    )
    
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Descripción detallada de la tarea",
        examples=["Recordar al equipo la reunión del lunes a las 10am"]
    )
    
    scheduled_datetime: datetime = Field(
        ...,
        description="Fecha y hora programada para el envío",
        examples=["2026-01-25T10:00:00Z"]
    )
    
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Etiquetas para clasificar la tarea",
        examples=[["importante", "equipo", "reunión"]]
    )
    
    @field_validator('scheduled_datetime')
    @classmethod
    def validate_future_date(cls, v: datetime) -> datetime:
        """
        Valida que la fecha programada sea futura.
        """
        if v <= datetime.now():
            raise ValueError('La fecha programada debe ser futura')
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """
        Valida que los tags cumplan con las restricciones.
        - Máximo 10 tags
        - Cada tag máximo 30 caracteres
        """
        if v is None:
            return v
        
        if len(v) > 10:
            raise ValueError('Máximo 10 tags permitidos')
        
        for tag in v:
            if len(tag) > 30:
                raise ValueError('Cada tag debe tener máximo 30 caracteres')
            if not tag.strip():
                raise ValueError('Los tags no pueden estar vacíos')
        
        # Limpiar espacios en blanco
        return [tag.strip() for tag in v]


# ============================================
# SCHEMA PARA CREAR TAREA
# ============================================
class TaskCreate(TaskBase):
    """
    Schema para CREAR una tarea.
    
    Incluye los IDs de los contactos a los que se enviará la tarea.
    """
    contact_ids: List[int] = Field(
        ...,
        min_length=1,
        description="Lista de IDs de contactos para asignar a la tarea",
        examples=[[1, 2, 3]]
    )
    
    @field_validator('contact_ids')
    @classmethod
    def validate_contact_ids(cls, v: List[int]) -> List[int]:
        """
        Valida que haya al menos un contacto.
        """
        if not v or len(v) < 1:
            raise ValueError('Debe asignar al menos un contacto a la tarea')
        return list(set(v))  # Eliminar duplicados


# ============================================
# SCHEMA PARA ACTUALIZAR TAREA
# ============================================
class TaskUpdate(BaseModel):
    """
    Schema para ACTUALIZAR una tarea.
    
    Todos los campos son opcionales.
    """
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    scheduled_datetime: Optional[datetime] = None
    tags: Optional[List[str]] = None
    status: Optional[TaskStatusEnum] = None
    is_sent: Optional[bool] = None
    sent_at: Optional[datetime] = None
    add_contact_ids: Optional[List[int]] = Field(
        None,
        description="IDs de contactos a agregar"
    )
    remove_contact_ids: Optional[List[int]] = Field(
        None,
        description="IDs de contactos a eliminar"
    )
    
    @field_validator('scheduled_datetime')
    @classmethod
    def validate_future_date_update(cls, v: Optional[datetime]) -> Optional[datetime]:
        """
        Valida que la fecha programada sea futura si se proporciona.
        """
        if v is not None and v <= datetime.now():
            raise ValueError('La fecha programada debe ser futura')
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags_update(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """
        Valida los tags si se proporcionan.
        """
        if v is not None:
            if len(v) > 10:
                raise ValueError('Máximo 10 tags permitidos')
            
            for tag in v:
                if len(tag) > 30:
                    raise ValueError('Cada tag debe tener máximo 30 caracteres')
                if not tag.strip():
                    raise ValueError('Los tags no pueden estar vacíos')
            
            return [tag.strip() for tag in v]
        return v


# ============================================
# SCHEMA DE RESPUESTA
# ============================================
class TaskResponse(BaseModel):
    """
    Schema de RESPUESTA cuando devolvemos una tarea.

    Incluye campos generados por la base de datos.
    """
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    scheduled_datetime: datetime
    status: TaskStatusEnum
    tags: Optional[str] = None
    tags_list: List[str] = Field(default_factory=list, description="Tags como lista")
    is_sent: bool
    sent_at: Optional[datetime] = None
    is_active: bool
    created_by_ai: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    history_count: int = Field(default=0, description="Cantidad de registros en historial")

    @classmethod
    def from_orm_with_tags(cls, obj: Any) -> 'TaskResponse':
        """
        Crea una TaskResponse desde un objeto ORM, convirtiendo tags a lista.
        """
        data = cls.model_validate(obj)
        if hasattr(obj, 'get_tags_list'):
            data.tags_list = obj.get_tags_list()
        elif data.tags:
            data.tags_list = [tag.strip() for tag in data.tags.split(',') if tag.strip()]
        return data
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "title": "Enviar recordatorio de reunión",
                "description": "Recordar al equipo la reunión del lunes",
                "scheduled_datetime": "2026-01-25T10:00:00Z",
                "tags": "importante,equipo",
                "tags_list": ["importante", "equipo"],
                "status": "pendiente",
                "is_sent": False,
                "sent_at": None,
                "is_active": True,
                "created_by_ai": False,
                "created_at": "2026-01-22T22:30:00",
                "updated_at": None,
                "history_count": 3
            }
        }
    )


# ============================================
# SCHEMA DE RESPUESTA CON CONTACTOS
# ============================================
class TaskWithContacts(TaskResponse):
    """
    Schema de respuesta que incluye los contactos asociados.
    """
    contacts: List[ContactResponse] = Field(
        default_factory=list,
        description="Contactos asignados a la tarea"
    )
    
    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================
# SCHEMA PARA AGREGAR/REMOVER CONTACTOS
# ============================================
class TaskContactsAdd(BaseModel):
    """
    Schema para agregar contactos a una tarea.
    """
    contact_ids: List[int] = Field(
        ...,
        min_length=1,
        description="IDs de contactos a agregar",
        examples=[[4, 5]]
    )
    
    @field_validator('contact_ids')
    @classmethod
    def validate_contact_ids(cls, v: List[int]) -> List[int]:
        if not v or len(v) < 1:
            raise ValueError('Debe especificar al menos un contacto')
        return list(set(v))


class TaskContactsRemove(BaseModel):
    """
    Schema para remover contactos de una tarea.
    """
    contact_ids: List[int] = Field(
        ...,
        min_length=1,
        description="IDs de contactos a remover",
        examples=[[3, 5]]
    )
    
    @field_validator('contact_ids')
    @classmethod
    def validate_contact_ids(cls, v: List[int]) -> List[int]:
        if not v or len(v) < 1:
            raise ValueError('Debe especificar al menos un contacto')
        return list(set(v))


# ============================================
# SCHEMA PARA CAMBIAR ESTADO
# ============================================
class TaskStatusUpdate(BaseModel):
    """
    Schema para cambiar el estado de una tarea.
    """
    status: TaskStatusEnum = Field(
        ...,
        description="Nuevo estado de la tarea",
        examples=["en_progreso"]
    )
