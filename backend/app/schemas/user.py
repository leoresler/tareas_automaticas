from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

"""
SCHEMAS DE USUARIO

Los schemas son como "moldes" que definen:
1. Qué datos acepta la API (UserCreate, UserUpdate)
2. Qué datos devuelve la API (UserResponse)
3. Cómo se validan esos datos (tipos, longitudes, formatos)

Pydantic se encarga de validar automáticamente:
- Tipos de datos correctos
- Formatos válidos (ej: email)
- Longitudes mínimas/máximas
- Campos obligatorios/opcionales
"""

# ============================================
# SCHEMA BASE (campos comunes)
# ============================================
class UserBase(BaseModel):
    """
    Schema base con campos comunes de usuario.
    Otros schemas heredan de este para evitar repetir código.
    """
    # EmailStr valida que sea un email válido (requiere email-validator)
    email: EmailStr = Field(..., description="Email único del usuario")
    
    # Field(...) significa que el campo es OBLIGATORIO
    # min_length=3: mínimo 3 caracteres
    # max_length=50: máximo 50 caracteres
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        description="Nombre de usuario único",
        examples=["johndoe"]
    )
    
    # Optional[str] significa que puede ser un string o None
    # Field(None) significa que por defecto es None (opcional)
    full_name: Optional[str] = Field(
        None, 
        max_length=200,
        description="Nombre completo del usuario",
        examples=["John Doe"]
    )


# ============================================
# SCHEMA PARA CREAR USUARIO (Registro)
# ============================================
class UserCreate(UserBase):
    """
    Schema para CREAR un usuario (registro).
    
    Incluye la contraseña en texto plano.
    La contraseña NUNCA se guarda así, se hashea antes de guardar en DB.
    """
    password: str = Field(
        ..., 
        min_length=8,
        description="Contraseña (mínimo 8 caracteres)",
        examples=["SecurePass123!"]
    )
    
    # Ejemplo de uso en la API:
    # POST /api/v1/auth/register
    # Body: {"email": "user@example.com", "username": "johndoe", "password": "pass123456"}


# ============================================
# SCHEMA PARA ACTUALIZAR USUARIO
# ============================================
class UserUpdate(BaseModel):
    """
    Schema para ACTUALIZAR un usuario.
    
    Todos los campos son opcionales porque el usuario
    puede querer actualizar solo uno o varios campos.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=200)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    
    # Ejemplo de uso:
    # PUT /api/v1/users/me
    # Body: {"full_name": "Juan Pérez"}  (solo actualiza el nombre)


# ============================================
# SCHEMA DE RESPUESTA (lo que devuelve la API)
# ============================================
class UserResponse(UserBase):
    """
    Schema de RESPUESTA cuando devolvemos un usuario.
    
    IMPORTANTE: NO incluye la contraseña por seguridad.
    Incluye campos adicionales que vienen de la DB (id, created_at, etc.)
    """
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # ConfigDict es la nueva forma de configurar Pydantic v2
    model_config = ConfigDict(
        from_attributes=True,  # Permite leer datos de objetos SQLAlchemy
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2026-01-22T19:00:00",
                "updated_at": None
            }
        }
    )


# ============================================
# SCHEMA PARA LOGIN
# ============================================
class UserLogin(BaseModel):
    """
    Schema para LOGIN.
    
    El usuario puede hacer login con username O email.
    """
    username_or_email: str = Field(
        ...,
        description="Username o email",
        examples=["johndoe", "user@example.com"]
    )
    password: str = Field(..., description="Contraseña")


# ============================================
# SCHEMA DE TOKEN (respuesta del login)
# ============================================
class Token(BaseModel):
    """
    Schema de respuesta cuando el usuario hace login exitosamente.
    """
    access_token: str = Field(..., description="Token JWT")
    token_type: str = Field(default="bearer", description="Tipo de token")
    user: UserResponse = Field(..., description="Datos del usuario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "johndoe",
                    "full_name": "John Doe",
                    "is_active": True,
                    "is_superuser": False,
                    "created_at": "2026-01-22T19:00:00"
                }
            }
        }
    )


# ============================================
# SCHEMA DE RESPUESTA DE LOGIN (con cookie)
# ============================================
class LoginResponse(BaseModel):
    """
    Schema de respuesta del login cuando el token se envía como cookie.
    """
    token_type: str = Field(default="bearer", description="Tipo de token")
    user: UserResponse = Field(..., description="Datos del usuario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "johndoe",
                    "full_name": "John Doe",
                    "is_active": True,
                    "is_superuser": False,
                    "created_at": "2026-01-22T19:00:00"
                }
            }
        }
    )


# ============================================
# SCHEMA PARA DECODIFICAR TOKEN
# ============================================
class TokenData(BaseModel):
    """
    Schema para los datos que van DENTRO del token JWT.
    """
    user_id: Optional[int] = None
    username: Optional[str] = None