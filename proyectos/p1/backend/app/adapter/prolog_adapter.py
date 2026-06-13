"""
prolog_adapter.py
Adaptador entre el backend Python y el motor de inferencia Prolog.

Responsabilidades:
  - Inicializar y mantener la instancia de Prolog.
  - Serializar/deserializar los tipos de pyswip a Python puro.
  - Exponer métodos de alto nivel para cada operación:
      * diagnosticar síntomas
      * CRUD de síntomas, fallas, recomendaciones y reglas
  - Persistir cambios del CRUD reescribiendo los archivos .pl.

Requisitos:
  pip install pyswip
  SWI-Prolog instalado en el sistema (swi-prolog.org)
"""

import os
import re
import threading
from pathlib import Path
from typing import Any

from pyswip import Prolog, Atom, Variable, Functor, call

# ── Rutas ────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
PROLOG_DIR = BASE_DIR / "p1/prolog"
ENGINE_PATH = PROLOG_DIR / "engine.pl"

DATA_FILES = {
    "sintoma":       PROLOG_DIR / "data" / "symptoms.pl",
    "falla":         PROLOG_DIR / "data" / "failures.pl",
    "recomendacion": PROLOG_DIR / "data" / "recommendations.pl",
    "regla":         PROLOG_DIR / "knowledge" / "rules.pl",
}

# /home/gio/Documentos/26S1/vacas/ia1_1S26V/-IA1-_VACASJUN2026_GiovanniConcoha_202100229/proyectos/prolog/engine.pl
# /home/gio/Documentos/26S1/vacas/ia1_1S26V/-IA1-_VACASJUN2026_GiovanniConcoha_202100229/proyectos/p1/prolog/engine.pl

# ── Singleton thread-safe ─────────────────────────────────────────────────────

_prolog: Prolog | None = None
_lock = threading.Lock()


def get_prolog() -> Prolog:
    """
    Devuelve la instancia única de Prolog.
    Carga engine.pl la primera vez.
    """
    global _prolog
    if _prolog is None:
        with _lock:
            if _prolog is None:
                p = Prolog()
                p.consult(str(ENGINE_PATH))
                _prolog = p
    return _prolog


def reload_prolog() -> None:
    """
    Fuerza la recarga del engine. Llamar después de
    modificar los archivos .pl por persistencia.
    """
    global _prolog
    with _lock:
        p = Prolog()
        p.consult(str(ENGINE_PATH))
        _prolog = p


# ── Helpers de conversión pyswip → Python ────────────────────────────────────

def _atom(value: Any) -> str:
    """Convierte Atom de pyswip o cualquier valor a str limpio."""
    if isinstance(value, Atom):
        return str(value)
    return str(value)


def _list_from_prolog(prolog_list: Any) -> list[str]:
    """
    Convierte una lista de Prolog (retornada por pyswip como lista Python
    de Atoms) a lista de strings Python.
    """
    if not prolog_list:
        return []
    return [_atom(item) for item in prolog_list]


def _functor_to_dict(term: Any) -> dict:
    """
    Convierte un término Functor de pyswip a dict.
    Solo para términos conocidos del engine.
    """
    if hasattr(term, "name") and hasattr(term, "args"):
        return {
            "functor": str(term.name),
            "args": [_atom(a) for a in term.args],
        }
    return {}


# ── Diagnóstico ───────────────────────────────────────────────────────────────

def diagnosticar(sintomas: list[str]) -> list[dict]:
    """
    Ejecuta el diagnóstico dado una lista de IDs de síntomas.

    Args:
        sintomas: Lista de IDs, e.g. ['S01', 'S03', 'S11']

    Returns:
        Lista de diagnósticos, cada uno:
        {
            "falla_id": str,
            "nombre": str,
            "tipo": str,
            "descripcion": str,
            "recomendaciones": [str, ...]
        }
    """
    prolog = get_prolog()

    # Construir lista Prolog como string: ['S01','S03','S11']
    sintomas_pl = "[" + ",".join(f"'{s}'" for s in sintomas) + "]"

    
    query = (
            f"diagnosticar({sintomas_pl}, "
            f"FallaID, Nombre, Tipo, Descripcion, Recomendaciones)"
        )


    resultados = []
    vistos=set()  # Para evitar duplicados si el motor retorna varias veces la misma falla
    for sol in prolog.query(query):
        falla_id = _atom(sol["FallaID"])

        # Evitar duplicados por FallaID
        if falla_id in vistos:
            continue
        vistos.add(falla_id)

        nombre = _atom(sol["Nombre"])
        tipo = _atom(sol["Tipo"])
        descripcion = _atom(sol["Descripcion"])
        recomendaciones = _list_from_prolog(sol["Recomendaciones"])

        resultados.append({
            "falla_id": falla_id,
            "nombre": nombre,
            "tipo": tipo,
            "descripcion": descripcion,
            "recomendaciones": recomendaciones,
        })

    return resultados



# ── Consultas de listado ───────────────────────────────────────────────────────

def listar_sintomas() -> list[dict]:
    """
    Devuelve todos los síntomas registrados en Prolog.

    Returns:
        [{"id": str, "nombre": str, "descripcion": str}, ...]
    """
    prolog = get_prolog()
    resultado = []
    
    # Consultar cada sintoma individualmente
    for sol in prolog.query("sintoma(ID, Nombre, Descripcion)"):
        resultado.append({
            "id":          _atom(sol["ID"]),
            "nombre":      _atom(sol["Nombre"]),
            "descripcion": _atom(sol["Descripcion"]),
        })

    return resultado



def listar_fallas() -> list[dict]:
    """
    Devuelve todas las fallas registradas en Prolog.

    Returns:
        [{"id": str, "nombre": str, "tipo": str, "descripcion": str}, ...]
    """
    prolog = get_prolog()
    resultado = []
    for sol in prolog.query("falla(ID, Nombre, Tipo, Descripcion)"):
        resultado.append({
            "id":          _atom(sol["ID"]),
            "nombre":      _atom(sol["Nombre"]),
            "tipo":        _atom(sol["Tipo"]),
            "descripcion": _atom(sol["Descripcion"]),
        })

    return resultado


def listar_recomendaciones() -> list[dict]:
    """
    Devuelve todas las recomendaciones registradas.

    Returns:
        [{"id": str, "falla_id": str, "descripcion": str}, ...]
    """
    prolog = get_prolog()
    resultado = []
    
    for sol in prolog.query("recomendacion(ID, FallaID, Descripcion)"):
        resultado.append({
            "id":          _atom(sol["ID"]),
            "falla_id":    _atom(sol["FallaID"]),
            "descripcion": _atom(sol["Descripcion"]),
        })

    return resultado


def listar_reglas() -> list[dict]:
    """
    Devuelve todas las reglas de diagnóstico.

    Returns:
        [{"falla_id": str, "sintomas": [str, ...]}, ...]
    """
    prolog = get_prolog()
    resultado = []
    
    for sol in prolog.query("diagnostico(FallaID, Sintomas)"):
        resultado.append({
            "falla_id": _atom(sol["FallaID"]),
            "sintomas": _list_from_prolog(sol["Sintomas"]),
        })

    return resultado


# ── CRUD: Síntomas ────────────────────────────────────────────────────────────

def agregar_sintoma(id_: str, nombre: str, descripcion: str) -> bool:
    """
    Agrega un síntoma a Prolog en memoria y lo persiste en symptoms.pl.

    Returns:
        True si se agregó, False si el ID ya existía.
    """
    prolog = get_prolog()
    query = f"agregar_sintoma('{id_}', '{_escape(nombre)}', '{_escape(descripcion)}')"
    ok = bool(list(prolog.query(query)))
    if ok:
        _persist_sintoma(id_, nombre, descripcion)
    return ok


def eliminar_sintoma(id_: str) -> bool:
    """Elimina un síntoma de Prolog y de symptoms.pl."""
    prolog = get_prolog()
    query = f"eliminar_sintoma('{id_}')"
    ok = bool(list(prolog.query(query)))
    if ok:
        _remove_fact_from_file(DATA_FILES["sintoma"], "sintoma", id_)
    return ok


# ── CRUD: Fallas ──────────────────────────────────────────────────────────────

def agregar_falla(id_: str, nombre: str, tipo: str, descripcion: str) -> bool:
    """Agrega una falla a Prolog y la persiste en failures.pl."""
    prolog = get_prolog()
    query = (
        f"agregar_falla('{id_}', '{_escape(nombre)}', "
        f"'{_escape(tipo)}', '{_escape(descripcion)}')"
    )
    ok = bool(list(prolog.query(query)))
    if ok:
        _persist_falla(id_, nombre, tipo, descripcion)
    return ok


def eliminar_falla(id_: str) -> bool:
    """Elimina una falla de Prolog y de failures.pl."""
    prolog = get_prolog()
    query = f"eliminar_falla('{id_}')"
    ok = bool(list(prolog.query(query)))
    if ok:
        _remove_fact_from_file(DATA_FILES["falla"], "falla", id_)
    return ok


# ── CRUD: Recomendaciones ─────────────────────────────────────────────────────

def agregar_recomendacion(id_: str, falla_id: str, descripcion: str) -> bool:
    """Agrega una recomendación a Prolog y la persiste en recommendations.pl."""
    prolog = get_prolog()
    query = (
        f"agregar_recomendacion('{id_}', '{falla_id}', '{_escape(descripcion)}')"
    )
    ok = bool(list(prolog.query(query)))
    if ok:
        _persist_recomendacion(id_, falla_id, descripcion)
    return ok


def eliminar_recomendacion(id_: str) -> bool:
    """Elimina una recomendación de Prolog y de recommendations.pl."""
    prolog = get_prolog()
    query = f"eliminar_recomendacion('{id_}')"
    ok = bool(list(prolog.query(query)))
    if ok:
        _remove_fact_from_file(DATA_FILES["recomendacion"], "recomendacion", id_)
    return ok


# ── CRUD: Reglas ──────────────────────────────────────────────────────────────

def agregar_regla(falla_id: str, sintomas: list[str]) -> bool:
    """
    Agrega una regla diagnóstico(FallaID, [S1,S2,...]) a Prolog y a rules.pl.

    Args:
        falla_id: ID de la falla, e.g. 'F01'
        sintomas: Lista de IDs de síntomas, e.g. ['S01', 'S03']
    """
    prolog = get_prolog()
    sintomas_pl = "[" + ",".join(f"'{s}'" for s in sintomas) + "]"
    query = f"agregar_regla('{falla_id}', {sintomas_pl})"
    ok = bool(list(prolog.query(query)))
    if ok:
        _persist_regla(falla_id, sintomas)
    return ok


def eliminar_regla(falla_id: str, sintomas: list[str]) -> bool:
    """Elimina una regla de Prolog y de rules.pl."""
    prolog = get_prolog()
    sintomas_pl = "[" + ",".join(f"'{s}'" for s in sintomas) + "]"
    query = f"eliminar_regla('{falla_id}', {sintomas_pl})"
    ok = bool(list(prolog.query(query)))
    if ok:
        _remove_rule_from_file(falla_id, sintomas)
    return ok


# ── Persistencia (escritura en archivos .pl) ──────────────────────────────────

def _escape(text: str) -> str:
    """Escapa comillas simples para embeber en strings Prolog."""
    return text.replace("'", "\\'")


def _persist_sintoma(id_: str, nombre: str, descripcion: str) -> None:
    path = DATA_FILES["sintoma"]
    line = f"\nsintoma('{id_}', '{_escape(nombre)}',\n    '{_escape(descripcion)}').\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def _persist_falla(id_: str, nombre: str, tipo: str, descripcion: str) -> None:
    path = DATA_FILES["falla"]
    line = (
        f"\nfalla('{id_}', '{_escape(nombre)}', '{_escape(tipo)}',\n"
        f"    '{_escape(descripcion)}').\n"
    )
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def _persist_recomendacion(id_: str, falla_id: str, descripcion: str) -> None:
    path = DATA_FILES["recomendacion"]
    line = f"\nrecomendacion('{id_}', '{falla_id}',\n    '{_escape(descripcion)}').\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def _persist_regla(falla_id: str, sintomas: list[str]) -> None:
    path = DATA_FILES["regla"]
    sintomas_pl = "[" + ", ".join(f"'{s}'" for s in sintomas) + "]"
    line = f"\ndiagnostico('{falla_id}', {sintomas_pl}).\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def _remove_fact_from_file(path: Path, functor: str, id_: str) -> None:
    """
    Elimina del archivo .pl todas las líneas que pertenezcan
    al hecho con el ID dado. Maneja hechos multi-línea buscando
    el bloque que comienza con functor('ID', ...
    """
    content = path.read_text(encoding="utf-8")
    # Reemplaza el bloque del hecho (puede ser multi-línea) terminado en ').
    pattern = rf"\n{functor}\('{re.escape(id_)}'[^.]*\)\."
    new_content = re.sub(pattern, "", content, flags=re.DOTALL)
    path.write_text(new_content, encoding="utf-8")


def _remove_rule_from_file(falla_id: str, sintomas: list[str]) -> None:
    """Elimina una regla específica de rules.pl."""
    path = DATA_FILES["regla"]
    sintomas_pl = "[" + ", ".join(f"'{s}'" for s in sintomas) + "]"
    content = path.read_text(encoding="utf-8")
    target = f"diagnostico('{falla_id}', {sintomas_pl})."
    new_content = content.replace("\n" + target, "").replace(target, "")
    path.write_text(new_content, encoding="utf-8")