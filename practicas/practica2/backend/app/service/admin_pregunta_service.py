from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.pregunta_repository import PreguntaRepository


class AdminPreguntaService:

    @staticmethod
    def _normalizar_palabras_clave(palabras):
        """
        Permite recibir:
        - lista: ["horario", "clases", "inscripción"]
        - string: "horario, clases, inscripción"
        """
        if palabras is None:
            return []

        if isinstance(palabras, str):
            palabras = palabras.split(",")

        palabras_limpias = []
        repetidas = set()

        for palabra in palabras:
            if palabra is None:
                continue

            palabra_limpia = palabra.strip()

            if not palabra_limpia:
                continue

            clave = palabra_limpia.lower()

            if clave not in repetidas:
                repetidas.add(clave)
                palabras_limpias.append(palabra_limpia)

        return palabras_limpias

    @staticmethod
    def listar_preguntas(db: Session):
        return PreguntaRepository.listar(db)

    @staticmethod
    def obtener_pregunta_por_id(
        db: Session,
        pregunta_id: int
    ):
        registro = PreguntaRepository.obtener_por_id(
            db,
            pregunta_id
        )

        if not registro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pregunta frecuente no encontrada"
            )

        return registro

    @staticmethod
    def listar_categorias(db: Session):
        return CategoriaRepository.listar(db)

    @staticmethod
    def crear_pregunta_frecuente(
        db: Session,
        pregunta: str,
        respuesta: str,
        categoria_id: int,
        palabras_clave
    ):
        if not pregunta or not pregunta.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La pregunta es obligatoria"
            )

        if not respuesta or not respuesta.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La respuesta es obligatoria"
            )

        categoria = CategoriaRepository.obtener_por_id(
            db,
            categoria_id
        )

        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La categoría indicada no existe"
            )

        palabras_limpias = AdminPreguntaService._normalizar_palabras_clave(
            palabras_clave
        )

        if len(palabras_limpias) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debes ingresar al menos una palabra clave"
            )

        nueva = PreguntaRepository.crear(
            db=db,
            pregunta=pregunta.strip(),
            respuesta=respuesta.strip(),
            categoria_id=categoria_id,
            palabras=palabras_limpias
        )

        return PreguntaRepository.obtener_por_id(
            db,
            nueva.id
        )

    @staticmethod
    def actualizar_pregunta_frecuente(
        db: Session,
        pregunta_id: int,
        pregunta: str,
        respuesta: str,
        categoria_id: int,
        palabras_clave
    ):
        existente = PreguntaRepository.obtener_por_id(
            db,
            pregunta_id
        )

        if not existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La pregunta frecuente no existe"
            )

        if not pregunta or not pregunta.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La pregunta es obligatoria"
            )

        if not respuesta or not respuesta.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La respuesta es obligatoria"
            )

        categoria = CategoriaRepository.obtener_por_id(
            db,
            categoria_id
        )

        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La categoría indicada no existe"
            )

        palabras_limpias = AdminPreguntaService._normalizar_palabras_clave(
            palabras_clave
        )

        if len(palabras_limpias) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debes ingresar al menos una palabra clave"
            )

        actualizada = PreguntaRepository.actualizar(
            db=db,
            pregunta_id=pregunta_id,
            pregunta=pregunta.strip(),
            respuesta=respuesta.strip(),
            categoria_id=categoria_id,
            palabras=palabras_limpias
        )

        if not actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se pudo actualizar la pregunta frecuente"
            )

        return PreguntaRepository.obtener_por_id(
            db,
            pregunta_id
        )

    @staticmethod
    def eliminar_pregunta_frecuente(
        db: Session,
        pregunta_id: int
    ):
        existente = PreguntaRepository.obtener_por_id(
            db,
            pregunta_id
        )

        if not existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La pregunta frecuente no existe"
            )

        eliminado = PreguntaRepository.eliminar(
            db,
            pregunta_id
        )

        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo eliminar la pregunta frecuente"
            )

        return {
            "message": "Pregunta frecuente eliminada correctamente"
        }