from pydantic import BaseModel
from typing import Optional


class ChatCreateRequest(BaseModel):
    chat_id: int
    nombre_chat: Optional[str]
    tipo_chat: Optional[str]
    activo: Optional[bool] = True


class ChatUpdateRequest(BaseModel):
    chat_id: int
    nombre_chat: Optional[str]
    tipo_chat: Optional[str]
    activo: Optional[bool] = True


class ChatResponse(BaseModel):
    id: int
    chat_id: int
    nombre_chat: Optional[str]
    tipo_chat: Optional[str]
    activo: bool

    class Config:
        orm_mode = True