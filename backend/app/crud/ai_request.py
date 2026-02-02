from sqlalchemy.orm import Session
from app.models.ai_request import AIRequest
from app.schemas.ai_request import AIRequestCreate
from typing import Optional, List

"""
CRUD DE SOLICITUD IA

Funciones para crear, actualizar y leer solicitudes de interpretación IA.
"""


# ============================================
# CREATE (Crear)
# ============================================

def create_ai_request(
    db: Session,
    user_id: int,
    input_text: str,
    input_type: str
) -> AIRequest:
    """
    Crea una nueva solicitud de interpretación IA.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario que hace la solicitud
        input_text: Texto o transcripción de audio
        input_type: Tipo de input (text o audio)
    
    Returns:
        Solicitud creada con todos sus datos
    """
    from app.models.ai_request import InputType
    
    # Convertir string a enum
    input_type_enum = InputType(input_type) if isinstance(input_type, str) else input_type
    
    db_request = AIRequest(
        user_id=user_id,
        input_text=input_text,
        input_type=input_type_enum,
        ai_response=None,
        interpreted_data=None,
        was_confirmed=False,
        tasks_created=None
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    return db_request


# ============================================
# READ (Leer)
# ============================================

def get_ai_requests_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[AIRequest]:
    """
    Obtiene todas las solicitudes de un usuario.
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        skip: Registros a saltar (paginación)
        limit: Máximo de registros
    
    Returns:
        Lista de solicitudes
    """
    return db.query(AIRequest).filter(
        AIRequest.user_id == user_id
    ).order_by(AIRequest.created_at.desc()).offset(skip).limit(limit).all()


# ============================================
# UPDATE (Actualizar)
# ============================================

def update_ai_request(
    db: Session,
    request_id: int,
    ai_response: Optional[str] = None,
    interpreted_data: Optional[str] = None
) -> Optional[AIRequest]:
    """
    Actualiza una solicitud de IA con la respuesta de la IA.
    
    Args:
        db: Sesión de base de datos
        request_id: ID de la solicitud
        ai_response: Respuesta completa de la IA
        interpreted_data: Datos interpretados (en JSON)
    
    Returns:
        Solicitud actualizada si existe, None si no
    """
    db_request = db.query(AIRequest).filter(
        AIRequest.id == request_id
    ).first()
    
    if not db_request:
        return None
    
    if ai_response is not None:
        db_request.ai_response = ai_response
    
    if interpreted_data is not None:
        db_request.interpreted_data = interpreted_data
    
    db.commit()
    db.refresh(db_request)
    
    return db_request


def confirm_ai_request(
    db: Session,
    request_id: int,
    tasks_created_ids: List[int]
) -> Optional[AIRequest]:
    """
    Confirma una solicitud de IA y marca las tareas creadas.
    
    Args:
        db: Sesión de base de datos
        request_id: ID de la solicitud
        tasks_created_ids: IDs de las tareas creadas
    
    Returns:
        Solicitud actualizada si existe, None si no
    """
    db_request = db.query(AIRequest).filter(
        AIRequest.id == request_id
    ).first()
    
    if not db_request:
        return None
    
    # Convertir lista a string
    tasks_created_str = ",".join(str(task_id) for task_id in tasks_created_ids) if tasks_created_ids else None
    
    db_request.was_confirmed = True
    db_request.tasks_created = tasks_created_str
    
    db.commit()
    db.refresh(db_request)
    
    return db_request
