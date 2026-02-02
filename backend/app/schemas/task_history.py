from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

"""
SCHEMAS DE HISTORIAL DE TAREA

Definen cómo se validan los datos de historial que entran y salen de la API.
"""

# ============================================
# SCHEMA BASE
# ============================================
class TaskHistoryBase(BaseModel):
    """
    Schema base con campos comunes de historial.
    """
    action: str = Field(
        ...,
        max_length=100,
        description="Acción realizada",
        examples=["creada", "modificada", "enviada", "estado_cambiado"]
    )
    
    field_changed: Optional[str] = Field(
        None,
        max_length=100,
        description="Campo que fue modificado",
        examples=["title", "status", "scheduled_datetime"]
    )
    
    old_value: Optional[str] = Field(
        None,
        description="Valor anterior (en JSON o texto)",
        examples=["Título anterior", "pendiente"]
    )
    
    new_value: Optional[str] = Field(
        None,
        description="Valor nuevo (en JSON o texto)",
        examples=["Nuevo título", "en_progreso"]
    )
    
    notes: Optional[str] = Field(
        None,
        description="Notas adicionales sobre la acción",
        examples=["Cambio solicitado por el usuario"]
    )


# ============================================
# SCHEMA PARA CREAR REGISTRO DE HISTORIAL
# ============================================
class TaskHistoryCreate(TaskHistoryBase):
    """
    Schema para CREAR un registro de historial.
    """
    pass


# ============================================
# SCHEMA DE RESPUESTA
# ============================================
class TaskHistoryResponse(TaskHistoryBase):
    """
    Schema de RESPUESTA cuando devolvemos un registro de historial.
    
    Incluye campos generados por la base de datos.
    """
    id: int
    task_id: int
    user_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "task_id": 1,
                "user_id": 1,
                "action": "creada",
                "field_changed": None,
                "old_value": None,
                "new_value": None,
                "notes": "Tarea creada desde la interfaz web",
                "created_at": "2026-01-22T22:30:00"
            }
        }
    )
