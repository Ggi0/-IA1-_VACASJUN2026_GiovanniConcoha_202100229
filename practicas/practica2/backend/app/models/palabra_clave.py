from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from app.config.db import Base


class PalabraClave(Base):

    __tablename__ = "palabras_clave"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    pregunta_id = Column(
        Integer,
        ForeignKey(
            "preguntas_frecuentes.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    palabra = Column(
        String(100),
        nullable=False
    )

    pregunta = relationship(
        "Pregunta",
        back_populates="palabras_clave"
    )