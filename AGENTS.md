# AGENTS.md

Este archivo proporciona guías para agentes de codificación que trabajan en este repositorio.

## 🚀 Comandos de Desarrollo y Build

### Backend (FastAPI + Python 3.11+)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (React + Vite + TypeScript)
```bash
cd frontend
npm install
npm run dev          # Servidor de desarrollo en http://localhost:5173
npm run build        # Build para producción
npm run lint         # Ejecutar ESLint
```

## 🧪 Testing

### Configuración de Tests Backend (Pytest)
```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx pytest-cov

# Ejecutar todos los tests
pytest

# Ejecutar tests con coverage
pytest --cov=app --cov-report=html

# Ejecutar un test específico
pytest tests/test_contacts.py::test_create_contact -v

# Ejecutar tests en un archivo específico
pytest tests/test_contacts.py -v
```

### Configuración de Tests Frontend (Vitest)
```bash
# Instalar Vitest
npm install -D vitest @testing-library/react @testing-library/jest-dom

# Ejecutar todos los tests
npm run test

# Ejecutar un test específico
npm run test -- contacts.test.ts

# Ejecutar en modo watch
npm run test -- --watch
```

## 📝 Convenciones de Código Python/Backend

### Docstrings
- Lenguaje: Español
- Secciones: `Args:`, `Returns:`, `Flujo:` (cuando sea necesario)
- Usar triple comillas dobles

```python
def create_contact(db: Session, contact: ContactCreate, user_id: int) -> Contact:
    """
    Crea un nuevo contacto en la base de datos.
    
    Args:
        db: Sesión de base de datos
        contact: Datos del contacto
        user_id: ID del usuario dueño del contacto
    
    Returns:
        Contacto creado con todos sus datos
    """
```

### Separadores de Sección
Usar el patrón `# ============================================` con título descriptivo:
```python
# ============================================
# CREATE (Crear)
# ============================================
```

### Type Hints
Obligatorios en todos los parámetros y valores de retorno:
```python
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
```

### Imports
Orden separado con líneas en blanco:
1. Biblioteca estándar
2. Terceros
3. Módulos locales

```python
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import User, Contact
from app.schemas import UserCreate
from app.crud import user as user_crud
```

### Nomenclatura
- Variables y funciones: `snake_case`
- Clases: `PascalCase`
- Constantes: `UPPER_SNAKE_CASE`

### Schemas Pydantic
Usar `Field()` para validaciones:
```python
from pydantic import BaseModel, Field, field_validator

class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    channel_type: ChannelTypeEnum = Field(...)
    
    @field_validator('channel_value')
    @classmethod
    def validate_channel_value(cls, v: str, info) -> str:
        # Validación personalizada
        return v
```

### Modelos SQLAlchemy
- Relaciones con `relationship()` y `back_populates`
- Timestamps automáticos: `server_default=func.now()` y `onupdate=func.now()`
- Soft delete con `is_active` en lugar de borrar registros

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### CRUD Separation
Separar lógica de base de datos en `app/crud/{resource}.py`:
```python
# CREATE, READ, UPDATE, DELETE con separadores
# ============================================
# CREATE (Crear)
# ============================================
def create_contact(db: Session, contact: ContactCreate) -> Contact:
    # Implementación
```

### Rutas API
API Router en `app/api/routes/{resource}.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact_in: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Implementación
```

### Error Handling
Usar `HTTPException` con códigos apropiados:
- 404: Recurso no encontrado
- 401: No autenticado
- 403: Sin permisos
- 400: Bad request
- 422: Error de validación

```python
if not contact:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Contacto no encontrado"
    )
```

## 🎨 Convenciones de Código TypeScript/Frontend

### Componentes React
Funcionales con arrow syntax:
```typescript
const App = () => {
  return (
    <div className="p-6">
      <h1>Componente App</h1>
    </div>
  )
}

export default App
```

### Estilos
Usar Tailwind CSS (v4) con clases utilitarias:
```typescript
<div className="p-4 bg-blue-500 text-white rounded-lg">
  Contenido
</div>
```

### TypeScript
- Strict mode habilitado en `tsconfig.json`
- Usar interfaces para tipos de datos:
```typescript
interface Contact {
  id: number
  name: string
  channel_type: 'whatsapp' | 'email' | 'telegram'
}
```

## 🗄️ Migraciones Alembic

### Crear migración
```bash
cd backend
alembic revision --autogenerate -m "descripción de la migración"
```

### Aplicar migraciones
```bash
alembic upgrade head
```

### Revertir migración
```bash
alembic downgrade -1
```

### Verificar estado
```bash
alembic current
alembic history
```

**Importante**: Asegúrate de que `alembic/env.py` importe correctamente todos los modelos desde `app.models` para que `--autogenerate` detecte los cambios.

## ⚙️ Configuración

### Backend
- Crear archivo `.env` basado en `.env.example`
- Variables críticas:
  - `DATABASE_URL`: MySQL connection string
  - `SECRET_KEY`: Para JWT tokens
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: Tiempo de expiración del token

### Database URL Format
```
mysql+pymysql://user:password@localhost:3306/database_name
```

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py          # Dependencias (get_db, get_current_user)
│   │   └── routes/          # Routers de API
│   ├── core/
│   │   ├── config.py        # Configuración central
│   │   └── security.py      # JWT y hash de contraseñas
│   ├── crud/                # Operaciones de base de datos
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Schemas Pydantic
│   ├── database.py          # Configuración de DB
│   └── main.py              # Aplicación FastAPI
frontend/
├── src/
│   ├── App.tsx
│   └── main.tsx
└── package.json
```
