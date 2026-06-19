from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.pregunta import Pregunta
from app.models.palabra_clave import PalabraClave

class PreguntaRepository:

    @staticmethod
    def listar(
        db: Session
    ):

        return (
            db.query(Pregunta)
            .options(
                joinedload(
                    Pregunta.categoria
                ),
                joinedload(
                    Pregunta.palabras_clave
                )
            )
            .all()
        )
    
    @staticmethod
    def obtener_por_id(
        db: Session,
        pregunta_id: int
    ):

        return (
            db.query(Pregunta)
            .options(
                joinedload(
                    Pregunta.categoria
                ),
                joinedload(
                    Pregunta.palabras_clave
                )
            )
            .filter(
                Pregunta.id == pregunta_id
            )
            .first()
        )
    
    @staticmethod
    def crear(
        db: Session,
        pregunta: str,
        respuesta: str,
        categoria_id: int,
        palabras: list[str]
    ):
        nueva = Pregunta(
            pregunta=pregunta,
            respuesta=respuesta,
            categoria_id=categoria_id
        )

        db.add(nueva)

        db.flush()

        for palabra in palabras:

            db.add(
                PalabraClave(
                    pregunta_id=nueva.id,
                    palabra=palabra
                )
            )

        db.commit()

        db.refresh(nueva)

        return nueva
    
    @staticmethod
    def actualizar(
        db: Session,
        pregunta_id: int,
        pregunta: str,
        respuesta: str,
        categoria_id: int,
        palabras: list[str]
    ):
        registro = (
            db.query(Pregunta)
            .filter(
                Pregunta.id == pregunta_id
            )
            .first()
        )

        if not registro:
            return None
        registro.pregunta = pregunta
        registro.respuesta = respuesta
        registro.categoria_id = categoria_id

        db.query(PalabraClave)\
            .filter(
                PalabraClave.pregunta_id
                == pregunta_id
            )\
            .delete()
        
        for palabra in palabras:

            db.add(
                PalabraClave(
                    pregunta_id=pregunta_id,
                    palabra=palabra
                )
            )

        db.commit()

        db.refresh(registro)

        return registro
    
    @staticmethod
    def eliminar(
        db: Session,
        pregunta_id: int
    ):

        registro = (
            db.query(Pregunta)
            .filter(
                Pregunta.id == pregunta_id
            )
            .first()
        )

        if not registro:
            return False

        db.delete(registro)

        db.commit()

        return True

    @staticmethod
    def buscar_por_palabra_clave(
        db: Session,
        texto: str
    ):
        """
        Busca preguntas activas cuyas palabras clave o el texto
        de la pregunta coincidan (parcialmente, sin importar mayúsculas)
        con el texto recibido.
        """
        from app.models.palabra_clave import PalabraClave

        texto_normalizado = texto.lower().strip()

        resultados = (
            db.query(Pregunta)
            .options(
                joinedload(Pregunta.categoria),
                joinedload(Pregunta.palabras_clave)
            )
            .join(PalabraClave, isouter=True)
            .filter(Pregunta.activa == True)
            .all()
        )

        coincidencias = []

        for pregunta in resultados:

            if texto_normalizado in pregunta.pregunta.lower():
                coincidencias.append(pregunta)
                continue

            for palabra in pregunta.palabras_clave:

                if palabra.palabra.lower() in texto_normalizado:
                    coincidencias.append(pregunta)
                    break

                if texto_normalizado in palabra.palabra.lower():
                    coincidencias.append(pregunta)
                    break

        return coincidencias