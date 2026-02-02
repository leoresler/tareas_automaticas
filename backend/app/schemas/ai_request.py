from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

"""
SCHEMAS DE SOLICITUD IA

Definen cómo se validan los datos de solicitudes IA que entran y salen de la API.
"""

# ============================================
# ENUM DE TIPO DE INPUT (para Pydantic)
# ============================================
class InputTypeEnum(str, Enum):
    """
    Enum para validación de tipos de input en Pydantic.
    Debe coincidir con el InputType de SQLAlchemy.
    """
    TEXT = "text"
    AUDIO = "audio"


# ============================================
# SCHEMA BASE
# ============================================
class AIRequestBase(BaseModel):
    """
    Schema base con campos comunes de solicitud IA.
    """
    input_text: str = Field(
        ...,
        min_length=1,
        description="Texto o transcripción de audio",
        examples=["Recordar a Juan la reunión del lunes a las 10am"]
    )
    
    input_type: InputTypeEnum = Field(
        ...,
        description="Tipo de input (text o audio)",
        examples=["text", "audio"]
    )


# ============================================
# SCHEMA PARA CREAR SOLICITUD
# ============================================
class AIRequestCreate(AIRequestBase):
    """
    Schema para CREAR una solicitud de interpretación IA.
    """
    pass


# ============================================
# SCHEMA DE RESPUESTA
# ============================================
class AIRequestResponse(BaseModel):
    """
    Schema de RESPUESTA cuando devolvemos una solicitud IA.
    
    Incluye campos generados por la base de datos.
    """
    id: int
    user_id: int
    input_text: str
    input_type: InputTypeEnum
    ai_response: Optional[str] = None
    interpreted_data: Optional[str] = None
    was_confirmed: bool
    tasks_created: Optional[str] = None
    tasks_created_list: List[int] = Field(default_factory=list, description="Lista de IDs de tareas creadas")
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "input_text": "Recordar a Juan la reunión del lunes",
                "input_type": "text",
                "ai_response": "Se detectó una tarea de reunión...",
                "interpreted_data": '{"tasks": [...]}',
                "was_confirmed": False,
                "tasks_created": None,
                "tasks_created_list": [],
                "created_at": "2026-01-22T22:30:00"
            }
        }
    )


# ============================================
# SCHEMA PARA CONFIRMAR SOLICITUD
# ============================================
class AIRequestConfirm(BaseModel):
    """
    Schema para confirmar una solicitud IA y crear las tareas.
    """
    tasks_created_ids: List[int] = Field(
        ...,
        min_length=1,
        description="IDs de las tareas creadas",
        examples=[[1, 2]]
    )
    
    @field_validator('tasks_created_ids')
    @classmethod
    def validate_task_ids(cls, v: List[int]) -> List[int]:
        if not v or len(v) < 1:
            raise ValueError('Debe especificar al menos una tarea creada')
        return list(set(v))
