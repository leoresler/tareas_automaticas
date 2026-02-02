from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

"""
SCHEMAS DE CONTACTO

Definen cómo se validan los datos de contactos que entran y salen de la API.
"""

# ============================================
# ENUM DE TIPOS DE CANAL (para Pydantic)
# ============================================
class ChannelTypeEnum(str, Enum):
    """
    Enum para validación de tipos de canal en Pydantic.
    Debe coincidir con el ChannelType de SQLAlchemy.
    """
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    TELEGRAM = "telegram"


# ============================================
# SCHEMA BASE (campos comunes)
# ============================================
class ContactBase(BaseModel):
    """
    Schema base con campos comunes de contacto.
    """
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre del contacto",
        examples=["Javier Pérez", "José García"]
    )
    
    channel_type: ChannelTypeEnum = Field(
        ...,
        description="Tipo de canal de comunicación",
        examples=["whatsapp", "email", "telegram"]
    )
    
    channel_value: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Valor del canal (teléfono, email, username)",
        examples=["+5491123456789", "contacto@empresa.com", "@username"]
    )
    
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Notas opcionales sobre el contacto",
        examples=["Contacto preferido para emergencias"]
    )


# ============================================
# SCHEMA PARA CREAR CONTACTO
# ============================================
class ContactCreate(ContactBase):
    """
    Schema para CREAR un contacto.
    
    Incluye validaciones específicas según el tipo de canal.
    """
    
    @field_validator('channel_value')
    @classmethod
    def validate_channel_value(cls, v: str, info) -> str:
        """
        Valida el formato del channel_value según el channel_type.
        
        Validaciones:
        - WhatsApp: Debe ser un número de teléfono con formato internacional
        - Email: Validación básica de formato
        - Telegram: Debe empezar con @
        """
        # Obtener el channel_type del contexto de validación
        channel_type = info.data.get('channel_type')
        
        if channel_type == ChannelTypeEnum.WHATSAPP:
            # Validar formato de teléfono para WhatsApp
            # Debe empezar con + y tener entre 10 y 15 dígitos
            v = v.strip()
            if not v.startswith('+'):
                raise ValueError('El número de WhatsApp debe empezar con + (formato internacional)')
            
            # Quitar el + para validar que el resto son dígitos
            phone_digits = v[1:].replace(' ', '').replace('-', '')
            if not phone_digits.isdigit():
                raise ValueError('El número de WhatsApp debe contener solo dígitos después del +')
            
            if len(phone_digits) < 10 or len(phone_digits) > 15:
                raise ValueError('El número de WhatsApp debe tener entre 10 y 15 dígitos')
        
        elif channel_type == ChannelTypeEnum.EMAIL:
            # Validación básica de email
            v = v.strip().lower()
            if '@' not in v or '.' not in v.split('@')[1]:
                raise ValueError('Formato de email inválido')
            
            # Validar que no tenga espacios
            if ' ' in v:
                raise ValueError('El email no puede contener espacios')
        
        elif channel_type == ChannelTypeEnum.TELEGRAM:
            # Validar formato de username de Telegram
            v = v.strip()
            if not v.startswith('@'):
                raise ValueError('El username de Telegram debe empezar con @')
            
            # Quitar @ para validar el username
            username = v[1:]
            if len(username) < 5:
                raise ValueError('El username de Telegram debe tener al menos 5 caracteres después de @')
            
            # Validar caracteres permitidos (letras, números, guiones bajos)
            if not username.replace('_', '').isalnum():
                raise ValueError('El username de Telegram solo puede contener letras, números y guiones bajos')
        
        return v


# ============================================
# SCHEMA PARA ACTUALIZAR CONTACTO
# ============================================
class ContactUpdate(BaseModel):
    """
    Schema para ACTUALIZAR un contacto.
    Todos los campos son opcionales.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    channel_type: Optional[ChannelTypeEnum] = None
    channel_value: Optional[str] = Field(None, min_length=3, max_length=255)
    notes: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None
    
    @field_validator('channel_value')
    @classmethod
    def validate_channel_value(cls, v: Optional[str], info) -> Optional[str]:
        """
        Valida el channel_value si se proporciona.
        Similar a ContactCreate pero permite None.
        """
        if v is None:
            return v
        
        channel_type = info.data.get('channel_type')
        
        # Si se actualiza channel_value sin channel_type, no validamos
        # (se validará con el tipo existente en el backend)
        if channel_type is None:
            return v
        
        # Aplicar las mismas validaciones que en ContactCreate
        if channel_type == ChannelTypeEnum.WHATSAPP:
            v = v.strip()
            if not v.startswith('+'):
                raise ValueError('El número de WhatsApp debe empezar con +')
            phone_digits = v[1:].replace(' ', '').replace('-', '')
            if not phone_digits.isdigit() or len(phone_digits) < 10 or len(phone_digits) > 15:
                raise ValueError('Formato de número de WhatsApp inválido')
        
        elif channel_type == ChannelTypeEnum.EMAIL:
            v = v.strip().lower()
            if '@' not in v or '.' not in v.split('@')[1] or ' ' in v:
                raise ValueError('Formato de email inválido')
        
        elif channel_type == ChannelTypeEnum.TELEGRAM:
            v = v.strip()
            if not v.startswith('@') or len(v) < 6:
                raise ValueError('Formato de username de Telegram inválido')
            username = v[1:]
            if not username.replace('_', '').isalnum():
                raise ValueError('Username de Telegram inválido')
        
        return v


# ============================================
# SCHEMA DE RESPUESTA
# ============================================
class ContactResponse(ContactBase):
    """
    Schema de RESPUESTA cuando devolvemos un contacto.
    
    Incluye campos generados por la base de datos.
    """
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "name": "Javier Pérez",
                "channel_type": "whatsapp",
                "channel_value": "+5491123456789",
                "notes": "Contacto de emergencia",
                "is_active": True,
                "created_at": "2026-01-22T22:30:00",
                "updated_at": None
            }
        }
    )
