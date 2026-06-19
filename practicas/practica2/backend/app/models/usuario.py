from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import func

from app.config.db import Base


class Usuario(Base):

    __tablename__ = "usuarios"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nombre = Column(
        String(100),
        nullable=False
    )

    usuario = Column(
        String(50),
        unique=True,
        nullable=False
    )

    correo = Column(
        String(150),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        Text,
        nullable=False
    )

    rol = Column(
        String(20),
        nullable=False
    )

    activo = Column(
        Boolean,
        default=True
    )

    fecha_creacion = Column(
        DateTime,
        server_default=func.now()
    )