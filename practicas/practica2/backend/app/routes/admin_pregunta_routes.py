from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.service.admin_pregunta_service import AdminPreguntaService
from app.schemas.pregunta_schema import *

router = APIRouter(prefix="/admin/preguntas", tags=["Preguntas Frecuentes"])


@router.get("/", response_model=list[PreguntaResponse])
def listar(db: Session = Depends(get_db)):
    return AdminPreguntaService.listar_preguntas(db)


@router.get("/{pregunta_id}", response_model=PreguntaResponse)
def obtener(pregunta_id: int, db: Session = Depends(get_db)):
    return AdminPreguntaService.obtener_pregunta_por_id(db, pregunta_id)


@router.post("/", response_model=PreguntaResponse)
def crear(data: PreguntaCreateRequest, db: Session = Depends(get_db)):
    return AdminPreguntaService.crear_pregunta_frecuente(
        db,
        data.pregunta,
        data.respuesta,
        data.categoria_id,
        data.palabras_clave
    )


@router.put("/{pregunta_id}", response_model=PreguntaResponse)
def actualizar(
    pregunta_id: int,
    data: PreguntaUpdateRequest,
    db: Session = Depends(get_db)
):
    return AdminPreguntaService.actualizar_pregunta_frecuente(
        db,
        pregunta_id,
        data.pregunta,
        data.respuesta,
        data.categoria_id,
        data.palabras_clave
    )


@router.delete("/{pregunta_id}")
def eliminar(pregunta_id: int, db: Session = Depends(get_db)):
    return AdminPreguntaService.eliminar_pregunta_frecuente(
        db,
        pregunta_id
    )