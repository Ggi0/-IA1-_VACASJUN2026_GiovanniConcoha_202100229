from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import relationship

from app.config.db import Base


class Categoria(Base):

    __tablename__ = "categorias"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nombre = Column(
        String(100),
        unique=True,
        nullable=False
    )

    descripcion = Column(
        Text
    )

    preguntas = relationship(
        "Pregunta",
        back_populates="categoria"
    )