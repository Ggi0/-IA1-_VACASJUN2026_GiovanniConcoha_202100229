from sqlalchemy.orm import Session

from app.models.telegram_chat import TelegramChat


class TelegramChatRepository:

    @staticmethod
    def listar(db: Session):
        return (
            db.query(TelegramChat)
            .order_by(TelegramChat.fecha_registro.desc())
            .all()
        )

    @staticmethod
    def obtener_por_id(db: Session, registro_id: int):
        return (
            db.query(TelegramChat)
            .filter(TelegramChat.id == registro_id)
            .first()
        )

    @staticmethod
    def obtener_por_chat_id(db: Session, chat_id: int):
        return (
            db.query(TelegramChat)
            .filter(TelegramChat.chat_id == chat_id)
            .first()
        )

    @staticmethod
    def crear(
        db: Session,
        chat_id: int,
        nombre_chat: str = None,
        tipo_chat: str = None,
        activo: bool = True
    ):
        nuevo = TelegramChat(
            chat_id=chat_id,
            nombre_chat=nombre_chat,
            tipo_chat=tipo_chat,
            activo=activo
        )

        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)

        return nuevo

    @staticmethod
    def actualizar(
        db: Session,
        registro_id: int,
        chat_id: int,
        nombre_chat: str = None,
        tipo_chat: str = None,
        activo: bool = True
    ):
        registro = (
            db.query(TelegramChat)
            .filter(TelegramChat.id == registro_id)
            .first()
        )

        if not registro:
            return None

        registro.chat_id = chat_id
        registro.nombre_chat = nombre_chat
        registro.tipo_chat = tipo_chat
        registro.activo = activo

        db.commit()
        db.refresh(registro)

        return registro

    @staticmethod
    def eliminar(
        db: Session,
        registro_id: int
    ):
        registro = (
            db.query(TelegramChat)
            .filter(TelegramChat.id == registro_id)
            .first()
        )

        if not registro:
            return False

        db.delete(registro)
        db.commit()

        return True