from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import func

from app.config.db import Base


class TelegramChat(Base):

    __tablename__ = "telegram_chats"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    chat_id = Column(
        BigInteger,
        unique=True,
        nullable=False
    )

    nombre_chat = Column(
        String(255)
    )

    tipo_chat = Column(
        String(50)
    )

    activo = Column(
        Boolean,
        default=True
    )

    fecha_registro = Column(
        DateTime,
        server_default=func.now()
    )