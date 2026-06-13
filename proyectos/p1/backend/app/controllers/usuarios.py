"""
controllers/usuarios.py
Capa HTTP para los endpoints del usuario final.
Usa FastAPI APIRouter — el main.py incluye este router.

Responsabilidades:
  - Recibir y validar el body/query params con Pydantic.
  - Llamar al service correspondiente.
  - Convertir el resultado del service a la respuesta HTTP correcta.
  - NO contiene lógica de negocio; eso vive en services/usuarios.py.

Registro en main.py:
    from app.controllers.usuarios import router as usuarios_router
    app.include_router(usuarios_router, prefix="/api")
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from app.services import usuarios as svc

router = APIRouter(tags=["Usuario"])


# ── Modelos de request ────────────────────────────────────────────────────────

class DiagnosticarRequest(BaseModel):
    sintomas: list[str]
    usuario: str | None = None
    mensaje: bool = True

    # Validación: la lista no puede estar vacía
    @field_validator("sintomas")
    @classmethod
    def al_menos_uno(cls, v):
        if not v:
            raise ValueError("Debe seleccionar al menos un síntoma.")
        return v


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/diagnosticar")
def diagnosticar(body: DiagnosticarRequest):
    """
    POST /api/diagnosticar
    Envía síntomas → obtiene diagnósticos + guarda historial + notifica Telegram.
    """
    resultado = svc.diagnosticar(body.sintomas, body.usuario, body.mensaje)

    # Si no hay diagnósticos, agregar mensaje informativo
    if not resultado["diagnosticos"]:
        resultado["mensaje"] = (
            "No se encontró un diagnóstico para los síntomas seleccionados."
        )

    return JSONResponse(status_code=200, content=resultado)


@router.get("/sintomas")
def listar_sintomas():
    """
    GET /api/sintomas
    Lista todos los síntomas disponibles para mostrar al usuario.
    """
    sintomas = svc.obtener_sintomas()
    return {"sintomas": sintomas}


@router.get("/historial")
def listar_historial(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    GET /api/historial?limit=20&offset=0
    Retorna diagnósticos paginados, del más reciente al más antiguo.
    """
    return svc.obtener_historial(limit=limit, offset=offset)


@router.get("/historial/{id}")
def detalle_historial(id: str):
    """
    GET /api/historial/{id}
    Retorna el detalle de un diagnóstico específico del historial.
    """
    entrada = svc.obtener_entrada_historial(id)
    if entrada is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Historial no encontrado."}
        )
    return entrada