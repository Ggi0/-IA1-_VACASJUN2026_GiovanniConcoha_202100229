"""
services/admin.py
Lógica de negocio para las operaciones del administrador.

Responsabilidades:
  - CRUD de síntomas, fallas y recomendaciones (delegando a prolog_adapter).
  - CRUD de reglas de diagnóstico (asociación síntoma ↔ falla).
  - Validaciones de negocio: IDs duplicados, existencia de referencias, etc.
  - Retorna dicts planos que el controller convierte a respuestas HTTP.

IMPORTANTE: Toda escritura aquí va directo a Prolog (memoria + archivo .pl).
No hay base de datos externa; Prolog ES la fuente de verdad.
"""

from app.adapter import prolog_adapter as prolog
from app.services.telegram import enviar_mensaje_personalizado


# SÍNTOMAS


def listar_sintomas() -> list[dict]:
    return prolog.listar_sintomas()


def crear_sintoma(id_: str, nombre: str, descripcion: str) -> dict:
    """
    Intenta agregar el síntoma a Prolog.
    El adapter ya verifica internamente que no exista el ID con \+.
    Retorna {"ok": True, "sintoma": {...}} o {"ok": False, "motivo": str}.
    """
    ok = prolog.agregar_sintoma(id_, nombre, descripcion)
    if not ok:
        return {"ok": False, "motivo": f"Ya existe un síntoma con el ID {id_}."}
    return {"ok": True, "sintoma": {"id": id_, "nombre": nombre, "descripcion": descripcion}}


def actualizar_sintoma(id_: str, nombre: str, descripcion: str) -> dict:
    """
    Update = eliminar el hecho antiguo + insertar el nuevo.
    Si el ID no existe, retorna error.
    """
    # Verificar existencia antes de intentar eliminar
    existentes = {s["id"] for s in prolog.listar_sintomas()}
    if id_ not in existentes:
        return {"ok": False, "motivo": f"Síntoma {id_} no encontrado."}

    prolog.eliminar_sintoma(id_)
    prolog.agregar_sintoma(id_, nombre, descripcion)
    return {"ok": True, "sintoma": {"id": id_, "nombre": nombre, "descripcion": descripcion}}


def eliminar_sintoma(id_: str) -> dict:
    """
    Elimina el síntoma. No elimina las reglas que lo referencian
    (eso queda a criterio del admin — el frontend puede advertirlo).
    """
    existentes = {s["id"] for s in prolog.listar_sintomas()}
    if id_ not in existentes:
        return {"ok": False, "motivo": f"Síntoma {id_} no encontrado."}

    prolog.eliminar_sintoma(id_)
    return {"ok": True}



# FALLAS


def listar_fallas() -> list[dict]:
    return prolog.listar_fallas()


def crear_falla(id_: str, nombre: str, tipo: str, descripcion: str) -> dict:
    ok = prolog.agregar_falla(id_, nombre, tipo, descripcion)
    if not ok:
        return {"ok": False, "motivo": f"Ya existe una falla con el ID {id_}."}
    return {"ok": True, "falla": {"id": id_, "nombre": nombre, "tipo": tipo, "descripcion": descripcion}}


def actualizar_falla(id_: str, nombre: str, tipo: str, descripcion: str) -> dict:
    existentes = {f["id"] for f in prolog.listar_fallas()}
    if id_ not in existentes:
        return {"ok": False, "motivo": f"Falla {id_} no encontrada."}

    prolog.eliminar_falla(id_)
    prolog.agregar_falla(id_, nombre, tipo, descripcion)
    return {"ok": True, "falla": {"id": id_, "nombre": nombre, "tipo": tipo, "descripcion": descripcion}}


def eliminar_falla(id_: str) -> dict:
    existentes = {f["id"] for f in prolog.listar_fallas()}
    if id_ not in existentes:
        return {"ok": False, "motivo": f"Falla {id_} no encontrada."}

    prolog.eliminar_falla(id_)
    # NOTA: Las reglas y recomendaciones asociadas a esta falla quedan huérfanas.
    # El frontend debería advertir esto al admin antes de confirmar el DELETE.
    return {"ok": True}



# RECOMENDACIONES


def listar_recomendaciones(falla_id: str | None = None) -> list[dict]:
    """
    Lista todas las recomendaciones. Si se pasa falla_id, filtra por ella.
    El filtro ocurre en Python porque el adapter ya trae todo.
    """
    todas = prolog.listar_recomendaciones()
    if falla_id:
        return [r for r in todas if r["falla_id"] == falla_id]
    return todas


def crear_recomendacion(id_: str, falla_id: str, descripcion: str) -> dict:
    # Validar que la falla referenciada exista antes de crear la recomendación
    fallas_existentes = {f["id"] for f in prolog.listar_fallas()}
    if falla_id not in fallas_existentes:
        return {"ok": False, "motivo": f"La falla {falla_id} no existe. Créela primero."}

    ok = prolog.agregar_recomendacion(id_, falla_id, descripcion)
    if not ok:
        return {"ok": False, "motivo": f"Ya existe una recomendación con el ID {id_}."}
    return {"ok": True, "recomendacion": {"id": id_, "falla_id": falla_id, "descripcion": descripcion}}


def actualizar_recomendacion(id_: str, falla_id: str, descripcion: str) -> dict:
    existentes = {r["id"] for r in prolog.listar_recomendaciones()}
    if id_ not in existentes:
        return {"ok": False, "motivo": f"Recomendación {id_} no encontrada."}

    # Validar que la falla nueva también exista
    fallas_existentes = {f["id"] for f in prolog.listar_fallas()}
    if falla_id not in fallas_existentes:
        return {"ok": False, "motivo": f"La falla {falla_id} no existe."}

    prolog.eliminar_recomendacion(id_)
    prolog.agregar_recomendacion(id_, falla_id, descripcion)
    return {"ok": True, "recomendacion": {"id": id_, "falla_id": falla_id, "descripcion": descripcion}}


def eliminar_recomendacion(id_: str) -> dict:
    existentes = {r["id"] for r in prolog.listar_recomendaciones()}
    if id_ not in existentes:
        return {"ok": False, "motivo": f"Recomendación {id_} no encontrada."}

    prolog.eliminar_recomendacion(id_)
    return {"ok": True}



# REGLAS (asociación síntoma ↔ falla)


def listar_reglas() -> list[dict]:
    return prolog.listar_reglas()


def crear_regla(falla_id: str, sintomas: list[str]) -> dict:
    """
    Validaciones antes de insertar la regla en Prolog:
      1. La falla debe existir.
      2. Todos los síntomas deben existir.
      3. La combinación falla_id + sintomas no debe ser duplicada.
    """
    # 1. Validar falla
    fallas_existentes = {f["id"] for f in prolog.listar_fallas()}
    if falla_id not in fallas_existentes:
        return {"ok": False, "motivo": f"La falla {falla_id} no existe. Créela primero."}

    # 2. Validar que todos los síntomas existan
    sintomas_existentes = {s["id"] for s in prolog.listar_sintomas()}
    faltantes = [s for s in sintomas if s not in sintomas_existentes]
    if faltantes:
        return {"ok": False, "motivo": f"Los siguientes síntomas no existen: {faltantes}"}

    # 3. Verificar duplicado: misma falla + misma lista de síntomas (mismo orden)
    reglas_actuales = prolog.listar_reglas()
    for regla in reglas_actuales:
        if regla["falla_id"] == falla_id and sorted(regla["sintomas"]) == sorted(sintomas):
            return {"ok": False, "motivo": f"Ya existe una regla {falla_id} ← {sintomas}."}

    ok = prolog.agregar_regla(falla_id, sintomas)
    if not ok:
        return {"ok": False, "motivo": "No se pudo agregar la regla en Prolog."}

    return {"ok": True, "regla": {"falla_id": falla_id, "sintomas": sintomas}}


def eliminar_regla(falla_id: str, sintomas: list[str]) -> dict:
    """
    Elimina la regla exacta falla_id ← [sintomas].
    La identificación es por falla + lista (no hay ID propio de regla).
    """
    reglas_actuales = prolog.listar_reglas()
    existe = any(
        r["falla_id"] == falla_id and sorted(r["sintomas"]) == sorted(sintomas)
        for r in reglas_actuales
    )
    if not existe:
        return {"ok": False, "motivo": "La regla especificada no existe."}

    prolog.eliminar_regla(falla_id, sintomas)
    return {"ok": True}


def enviar_mensaje_telegram(mensaje: str) -> bool:

    if not mensaje.strip():
        return False

    return enviar_mensaje_personalizado(mensaje)