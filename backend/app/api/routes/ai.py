from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.schemas.ai_request import (
    AIRequestCreate,
    AIRequestResponse,
    AIRequestConfirm,
    InputTypeEnum
)
from app.crud import ai_request as ai_request_crud
from app.crud import task as task_crud
from app.models.user import User

"""
ENDPOINTS DE INTELIGENCIA ARTIFICIAL

Este router maneja:
- Interpretar texto/audio para crear tareas
- Confirmar interpretación de IA
- Obtener historial de solicitudes
"""

router = APIRouter()


# ============================================
# INTERPRETAR TEXTO/AUDIO
# ============================================

@router.post("/interpret", response_model=AIRequestResponse, status_code=status.HTTP_201_CREATED)
def interpret_text(
    request_in: AIRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Interpreta texto o transcripción de audio para crear tareas.
    
    **Ejemplo de uso:**
    - Usuario escribe: "Recordar a Juan la reunión del lunes a las 10am"
    - IA interpreta: Tarea de reunión para contacto Juan el lunes a las 10am
    
    **Proceso:**
    1. Guarda la solicitud en la base de datos
    2. Interpreta el texto (mock por ahora)
    3. Devuelve datos interpretados
    4. Usuario puede confirmar para crear las tareas
    
    Request body:
```json
    {
        "input_text": "Recordar a Juan la reunión del lunes a las 10am",
        "input_type": "text"
    }
```
    """
    # Crear la solicitud
    ai_request = ai_request_crud.create_ai_request(
        db=db,
        user_id=current_user.id,
        input_text=request_in.input_text,
        input_type=request_in.input_type.value
    )
    
    # Mock de respuesta de IA (en producción, esto llamaría a un servicio de IA real)
    # Por ahora, generamos una interpretación básica del texto
    mock_ai_response = f"Interpretación de: {request_in.input_text}"
    mock_interpreted_data = '{"tasks": [{"title": "Tarea generada", "description": request_in.input_text, "scheduled_datetime": "2026-01-25T10:00:00Z", "contacts": []}]}'
    
    # Actualizar con respuesta de IA
    ai_request = ai_request_crud.update_ai_request(
        db=db,
        request_id=ai_request.id,
        ai_response=mock_ai_response,
        interpreted_data=mock_interpreted_data
    )
    
    # Preparar respuesta
    ai_request_dict = ai_request.__dict__.copy()
    ai_request_dict['tasks_created_list'] = []
    
    return AIRequestResponse(**ai_request_dict)


# ============================================
# CONFIRMAR SOLICITUD Y CREAR TAREAS
# ============================================

@router.post("/confirm/{request_id}", response_model=AIRequestResponse)
def confirm_ai_request(
    request_id: int,
    confirm_data: AIRequestConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Confirma una solicitud de IA y crea las tareas basadas en la interpretación.
    
    **Proceso:**
    1. Busca la solicitud de IA
    2. Verifica que pertenezca al usuario
    3. Crea las tareas basadas en los datos interpretados
    4. Marca la solicitud como confirmada
    5. Guarda los IDs de las tareas creadas
    
    Request body:
```json
    {
        "tasks_created_ids": [1, 2, 3]
    }
```
    
    **Respuesta:**
    ```json
    {
        "id": 1,
        "user_id": 1,
        "input_text": "Recordar a Juan...",
        "input_type": "text",
        "ai_response": "...",
        "interpreted_data": "...",
        "was_confirmed": true,
        "tasks_created": "1,2,3",
        "tasks_created_list": [1, 2, 3],
        "created_at": "2026-01-22T22:30:00"
    }
    ```
    """
    # Verificar que la solicitud pertenezca al usuario
    from app.models.ai_request import AIRequest
    ai_request = db.query(AIRequest).filter(
        AIRequest.id == request_id,
        AIRequest.user_id == current_user.id
    ).first()
    
    if not ai_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    
    if ai_request.was_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta solicitud ya fue confirmada"
        )
    
    # Confirmar y guardar IDs de tareas
    ai_request = ai_request_crud.confirm_ai_request(
        db=db,
        request_id=request_id,
        tasks_created_ids=confirm_data.tasks_created_ids
    )
    
    # Preparar respuesta
    ai_request_dict = ai_request.__dict__.copy()
    ai_request_dict['tasks_created_list'] = confirm_data.tasks_created_ids
    
    return AIRequestResponse(**ai_request_dict)


# ============================================
# HISTORIAL DE SOLICITUDES
# ============================================

@router.get("/requests", response_model=List[AIRequestResponse])
def get_ai_requests(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Máximo de registros"),
    was_confirmed: Optional[bool] = Query(None, description="Filtrar por confirmación"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el historial de solicitudes de IA del usuario.
    
    **Filtros opcionales:**
    - `was_confirmed`: true (solo confirmadas), false (no confirmadas), null (todas)
    - `skip` y `limit`: Para paginación
    
    **Ejemplos:**
    - `/api/v1/ai/requests` - Todas las solicitudes
    - `/api/v1/ai/requests?was_confirmed=false` - Solo no confirmadas
    - `/api/v1/ai/requests?skip=10&limit=20` - Página 2
    """
    # Obtener solicitudes del usuario
    from app.models.ai_request import AIRequest
    
    query = db.query(AIRequest).filter(
        AIRequest.user_id == current_user.id
    )
    
    # Aplicar filtro opcional
    if was_confirmed is not None:
        query = query.filter(AIRequest.was_confirmed == was_confirmed)
    
    # Ordenar por fecha descendente
    query = query.order_by(AIRequest.created_at.desc())
    
    requests = query.offset(skip).limit(limit).all()
    
    # Agregar tasks_created_list a cada solicitud
    result = []
    for req in requests:
        req_dict = req.__dict__.copy()
        if req.tasks_created:
            req_dict['tasks_created_list'] = [int(tid) for tid in req.tasks_created.split(",")]
        else:
            req_dict['tasks_created_list'] = []
        result.append(AIRequestResponse(**req_dict))
    
    return result
