"""
Schemas de validación Pydantic
"""
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenData
)

from .contact import (
    ChannelTypeEnum,
    ContactBase,
    ContactCreate,
    ContactUpdate,
    ContactResponse
)

from .task import (
    TaskStatusEnum,
    TaskBase,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskWithContacts,
    TaskContactsAdd,
    TaskContactsRemove,
    TaskStatusUpdate
)

from .task_history import (
    TaskHistoryBase,
    TaskHistoryCreate,
    TaskHistoryResponse
)

from .ai_request import (
    InputTypeEnum,
    AIRequestBase,
    AIRequestCreate,
    AIRequestResponse,
    AIRequestConfirm
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate", 
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenData",
    
    # Contact schemas
    "ChannelTypeEnum",
    "ContactBase",
    "ContactCreate",
    "ContactUpdate",
    "ContactResponse",
    
    # Task schemas
    "TaskStatusEnum",
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskWithContacts",
    "TaskContactsAdd",
    "TaskContactsRemove",
    "TaskStatusUpdate",
    
    # TaskHistory schemas
    "TaskHistoryBase",
    "TaskHistoryCreate",
    "TaskHistoryResponse",
    
    # AIRequest schemas
    "InputTypeEnum",
    "AIRequestBase",
    "AIRequestCreate",
    "AIRequestResponse",
    "AIRequestConfirm"
]