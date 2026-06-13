"""
controllers/admin.py
Capa HTTP para los endpoints del administrador (CRUD completo).
Usa FastAPI APIRouter — el main.py incluye este router.

Responsabilidades:
  - Recibir y validar bodies con Pydantic.
  - Llamar al service admin y traducir {"ok", "motivo"} a status HTTP correcto.
  - NO contiene validaciones de negocio; esas viven en services/admin.py.

Registro en main.py:
    from app.controllers.admin import router as admin_router
    app.include_router(admin_router, prefix="/api")

Convención de respuesta de error del service:
    {"ok": False, "motivo": "..."} → el controller decide el status code
    {"ok": True, ...}             → 200 o 201
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services import admin as svc

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Helper: traducir resultado del service a JSON response ────────────────────

def _error(motivo: str, status: int) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": motivo})



# SÍNTOMAS


class SintomaBody(BaseModel):
    id: str
    nombre: str
    descripcion: str

class SintomaUpdateBody(BaseModel):
    nombre: str
    descripcion: str


@router.get("/sintomas")
def listar_sintomas():
    """GET /api/admin/sintomas"""
    return {"sintomas": svc.listar_sintomas()}


@router.post("/sintomas", status_code=201)
def crear_sintoma(body: SintomaBody):
    """POST /api/admin/sintomas"""
    res = svc.crear_sintoma(body.id, body.nombre, body.descripcion)
    if not res["ok"]:
        # 409 Conflict: ID duplicado
        return _error(res["motivo"], 409)
    return JSONResponse(
        status_code=201,
        content={"mensaje": f"Síntoma {body.id} agregado correctamente.", "sintoma": res["sintoma"]}
    )


@router.put("/sintomas/{id}")
def actualizar_sintoma(id: str, body: SintomaUpdateBody):
    """PUT /api/admin/sintomas/{id}"""
    res = svc.actualizar_sintoma(id, body.nombre, body.descripcion)
    if not res["ok"]:
        return _error(res["motivo"], 404)
    return {"mensaje": f"Síntoma {id} actualizado correctamente.", "sintoma": res["sintoma"]}


@router.delete("/sintomas/{id}")
def eliminar_sintoma(id: str):
    """DELETE /api/admin/sintomas/{id}"""
    res = svc.eliminar_sintoma(id)
    if not res["ok"]:
        return _error(res["motivo"], 404)
    return {"mensaje": f"Síntoma {id} eliminado correctamente."}



# FALLAS


class FallaBody(BaseModel):
    id: str
    nombre: str
    tipo: str
    descripcion: str

class FallaUpdateBody(BaseModel):
    nombre: str
    tipo: str
    descripcion: str


@router.get("/fallas")
def listar_fallas():
    """GET /api/admin/fallas"""
    return {"fallas": svc.listar_fallas()}


@router.post("/fallas", status_code=201)
def crear_falla(body: FallaBody):
    """POST /api/admin/fallas"""
    res = svc.crear_falla(body.id, body.nombre, body.tipo, body.descripcion)
    if not res["ok"]:
        return _error(res["motivo"], 409)
    return JSONResponse(
        status_code=201,
        content={"mensaje": f"Falla {body.id} agregada correctamente.", "falla": res["falla"]}
    )


@router.put("/fallas/{id}")
def actualizar_falla(id: str, body: FallaUpdateBody):
    """PUT /api/admin/fallas/{id}"""
    res = svc.actualizar_falla(id, body.nombre, body.tipo, body.descripcion)
    if not res["ok"]:
        return _error(res["motivo"], 404)
    return {"mensaje": f"Falla {id} actualizada correctamente.", "falla": res["falla"]}


@router.delete("/fallas/{id}")
def eliminar_falla(id: str):
    """
    DELETE /api/admin/fallas/{id}
    ADVERTENCIA: No elimina automáticamente reglas/recomendaciones asociadas.
    El frontend debe advertir esto al admin antes de confirmar.
    """
    res = svc.eliminar_falla(id)
    if not res["ok"]:
        return _error(res["motivo"], 404)
    return {"mensaje": f"Falla {id} eliminada correctamente."}



# RECOMENDACIONES


class RecomendacionBody(BaseModel):
    id: str
    falla_id: str
    descripcion: str

class RecomendacionUpdateBody(BaseModel):
    falla_id: str
    descripcion: str


@router.get("/recomendaciones")
def listar_recomendaciones(falla_id: str | None = Query(default=None)):
    """
    GET /api/admin/recomendaciones
    GET /api/admin/recomendaciones?falla_id=F01
    """
    return {"recomendaciones": svc.listar_recomendaciones(falla_id)}


@router.post("/recomendaciones", status_code=201)
def crear_recomendacion(body: RecomendacionBody):
    """POST /api/admin/recomendaciones"""
    res = svc.crear_recomendacion(body.id, body.falla_id, body.descripcion)
    if not res["ok"]:
        # 400 si la falla no existe, 409 si el ID ya existe
        status = 400 if "no existe" in res["motivo"] else 409
        return _error(res["motivo"], status)
    return JSONResponse(
        status_code=201,
        content={
            "mensaje": f"Recomendación {body.id} agregada correctamente.",
            "recomendacion": res["recomendacion"]
        }
    )


@router.put("/recomendaciones/{id}")
def actualizar_recomendacion(id: str, body: RecomendacionUpdateBody):
    """PUT /api/admin/recomendaciones/{id}"""
    res = svc.actualizar_recomendacion(id, body.falla_id, body.descripcion)
    if not res["ok"]:
        status = 404 if "no encontrada" in res["motivo"] else 400
        return _error(res["motivo"], status)
    return {
        "mensaje": f"Recomendación {id} actualizada correctamente.",
        "recomendacion": res["recomendacion"]
    }


@router.delete("/recomendaciones/{id}")
def eliminar_recomendacion(id: str):
    """DELETE /api/admin/recomendaciones/{id}"""
    res = svc.eliminar_recomendacion(id)
    if not res["ok"]:
        return _error(res["motivo"], 404)
    return {"mensaje": f"Recomendación {id} eliminada correctamente."}



# REGLAS (asociación síntoma ↔ falla)


class ReglaBody(BaseModel):
    falla_id: str
    sintomas: list[str]


@router.get("/reglas")
def listar_reglas():
    """GET /api/admin/reglas"""
    return {"reglas": svc.listar_reglas()}


@router.post("/reglas", status_code=201)
def crear_regla(body: ReglaBody):
    """
    POST /api/admin/reglas
    Asocia una lista de síntomas a una falla como regla de diagnóstico.
    1 síntoma  = diagnóstico por síntoma único.
    2-3 síntomas = diagnóstico combinado.
    """
    res = svc.crear_regla(body.falla_id, body.sintomas)
    if not res["ok"]:
        status = 409 if "Ya existe" in res["motivo"] else 400
        return _error(res["motivo"], status)
    return JSONResponse(
        status_code=201,
        content={
            "mensaje": f"Regla agregada correctamente: {body.falla_id} ← {body.sintomas}",
            "regla": res["regla"]
        }
    )


@router.delete("/reglas")
def eliminar_regla(body: ReglaBody):
    """
    DELETE /api/admin/reglas
    Body requerido: { "falla_id": "F01", "sintomas": ["S01", "S03"] }
    Las reglas se identifican por falla + lista de síntomas (no tienen ID propio).
    """
    res = svc.eliminar_regla(body.falla_id, body.sintomas)
    if not res["ok"]:
        return _error(res["motivo"], 404)
    return {"mensaje": f"Regla {body.falla_id} ← {body.sintomas} eliminada correctamente."}