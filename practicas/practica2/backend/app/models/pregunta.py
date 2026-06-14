from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func

from sqlalchemy.orm import relationship

from app.config.db import Base


class Pregunta(Base):

    __tablename__ = "preguntas_frecuentes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    pregunta = Column(
        Text,
        nullable=False
    )

    respuesta = Column(
        Text,
        nullable=False
    )

    categoria_id = Column(
        Integer,
        ForeignKey("categorias.id"),
        nullable=False
    )

    activa = Column(
        Boolean,
        default=True
    )

    fecha_creacion = Column(
        DateTime,
        server_default=func.now()
    )

    categoria = relationship(
        "Categoria",
        back_populates="preguntas"
    )

    palabras_clave = relationship(
        "PalabraClave",
        back_populates="pregunta",
        cascade="all, delete-orphan"
    )