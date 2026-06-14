from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import func

from app.config.db import Base


class Consulta(Base):

    __tablename__ = "consultas"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    chat_id = Column(
        BigInteger,
        nullable=False
    )

    pregunta_realizada = Column(
        Text,
        nullable=False
    )

    respuesta_entregada = Column(
        Text
    )

    fecha_consulta = Column(
        DateTime,
        server_default=func.now()
    )