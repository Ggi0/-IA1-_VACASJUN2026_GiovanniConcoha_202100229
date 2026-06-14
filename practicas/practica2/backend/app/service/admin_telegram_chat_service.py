from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.telegram_chat_repository import TelegramChatRepository


class AdminTelegramChatService:

    @staticmethod
    def listar_chats_autorizados(db: Session):
        return TelegramChatRepository.listar(db)

    @staticmethod
    def obtener_chat_por_id(
        db: Session,
        registro_id: int
    ):
        registro = TelegramChatRepository.obtener_por_id(
            db,
            registro_id
        )

        if not registro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro de chat no encontrado"
            )

        return registro

    @staticmethod
    def registrar_chat_autorizado(
        db: Session,
        chat_id: int,
        nombre_chat: str = None,
        tipo_chat: str = None,
        activo: bool = True
    ):
        if chat_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El chat_id es obligatorio"
            )

        existente = TelegramChatRepository.obtener_por_chat_id(
            db,
            chat_id
        )

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ese chat_id ya está registrado"
            )

        return TelegramChatRepository.crear(
            db=db,
            chat_id=chat_id,
            nombre_chat=nombre_chat.strip() if nombre_chat else None,
            tipo_chat=tipo_chat.strip() if tipo_chat else None,
            activo=activo
        )

    @staticmethod
    def actualizar_chat_autorizado(
        db: Session,
        registro_id: int,
        chat_id: int,
        nombre_chat: str = None,
        tipo_chat: str = None,
        activo: bool = True
    ):
        registro = TelegramChatRepository.obtener_por_id(
            db,
            registro_id
        )

        if not registro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro de chat no encontrado"
            )

        otro = TelegramChatRepository.obtener_por_chat_id(
            db,
            chat_id
        )

        if otro and otro.id != registro_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ese chat_id ya pertenece a otro registro"
            )

        actualizado = TelegramChatRepository.actualizar(
            db=db,
            registro_id=registro_id,
            chat_id=chat_id,
            nombre_chat=nombre_chat.strip() if nombre_chat else None,
            tipo_chat=tipo_chat.strip() if tipo_chat else None,
            activo=activo
        )

        if not actualizado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar el chat autorizado"
            )

        return actualizado

    @staticmethod
    def eliminar_chat_autorizado(
        db: Session,
        registro_id: int
    ):
        registro = TelegramChatRepository.obtener_por_id(
            db,
            registro_id
        )

        if not registro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro de chat no encontrado"
            )

        eliminado = TelegramChatRepository.eliminar(
            db,
            registro_id
        )

        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo eliminar el chat autorizado"
            )

        return {
            "message": "Chat autorizado eliminado correctamente"
        }

    @staticmethod
    def chat_esta_autorizado(
        db: Session,
        chat_id: int
    ) -> bool:
        """
        Este método te va a servir después para el servicio del bot.
        """
        registro = TelegramChatRepository.obtener_por_chat_id(
            db,
            chat_id
        )

        if not registro:
            return False

        return registro.activo is True