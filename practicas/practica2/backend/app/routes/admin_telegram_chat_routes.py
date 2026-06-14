from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.service.admin_telegram_chat_service import AdminTelegramChatService
from app.schemas.telegram_chat_schema import *

router = APIRouter(
    prefix="/admin/chats",
    tags=["Chats Autorizados"]
)


@router.get("/", response_model=list[ChatResponse])
def listar(db: Session = Depends(get_db)):
    return AdminTelegramChatService.listar_chats_autorizados(db)


@router.get("/{id}", response_model=ChatResponse)
def obtener(id: int, db: Session = Depends(get_db)):
    return AdminTelegramChatService.obtener_chat_por_id(db, id)


@router.post("/", response_model=ChatResponse)
def crear(data: ChatCreateRequest, db: Session = Depends(get_db)):
    return AdminTelegramChatService.registrar_chat_autorizado(
        db,
        data.chat_id,
        data.nombre_chat,
        data.tipo_chat,
        data.activo
    )


@router.put("/{id}", response_model=ChatResponse)
def actualizar(id: int, data: ChatUpdateRequest, db: Session = Depends(get_db)):
    return AdminTelegramChatService.actualizar_chat_autorizado(
        db,
        id,
        data.chat_id,
        data.nombre_chat,
        data.tipo_chat,
        data.activo
    )


@router.delete("/{id}")
def eliminar(id: int, db: Session = Depends(get_db)):
    return AdminTelegramChatService.eliminar_chat_autorizado(
        db,
        id
    )