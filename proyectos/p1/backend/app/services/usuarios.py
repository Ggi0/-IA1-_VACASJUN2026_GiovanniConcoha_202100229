"""
services/usuarios.py
Lógica de negocio para las operaciones del usuario final.

Responsabilidades:
  - Orquestar el diagnóstico: llama al adapter, guarda historial, notifica Telegram.
  - Leer y paginar el historial desde historial.json.
  - NO sabe nada de HTTP (eso es responsabilidad del controller).
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from app.adapter import prolog_adapter as prolog
from app.services.telegram import enviar_diagnostico

# ── Ruta del historial ────────────────────────────────────────────────────────

HISTORIAL_PATH = Path(__file__).parent / "historial" / "historial.json"


# ── Helpers de historial ──────────────────────────────────────────────────────

def _leer_historial() -> list[dict]:
    """Lee el archivo JSON completo. Retorna lista vacía si está vacío o no existe."""
    if not HISTORIAL_PATH.exists():
        return []
    content = HISTORIAL_PATH.read_text(encoding="utf-8").strip()
    if not content or content == "[]":
        return []
    return json.loads(content)


def _guardar_entrada(entrada: dict) -> None:
    """
    Agrega una nueva entrada al historial SIN sobrescribir las existentes.
    Lee el archivo, hace append y vuelve a escribir.
    """
    historial = _leer_historial()
    historial.append(entrada)
    HISTORIAL_PATH.write_text(
        json.dumps(historial, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


# ── Servicio principal: diagnosticar ─────────────────────────────────────────

def diagnosticar(sintomas: list[str], usuario: str | None = None, mensaje: bool = True) -> dict:
    """
    Orquesta el diagnóstico completo:
      1. Llama a Prolog via adapter para obtener diagnósticos.
      2. Construye la entrada de historial.
      3. Persiste en historial.json.
      4. (Placeholder) Notifica por Telegram.
      5. Retorna la respuesta lista para el controller.

    Args:
        sintomas: Lista de IDs de síntomas, e.g. ['S01', 'S11']
        usuario:  Nombre opcional del usuario para el historial.

    Returns:
        dict con claves: diagnosticos, historial_id, telegram_enviado
    """

    # 1. Motor Prolog — toda la lógica de inferencia ocurre aquí
    diagnosticos = prolog.diagnosticar(sintomas)

    # 2. Construir entrada del historial
    historial_id = str(uuid.uuid4())
    entrada = {
        "id": historial_id,
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "usuario": usuario or "Anónimo",
        "sintomas_seleccionados": sintomas,
        "diagnosticos": diagnosticos,      # lista de dicts ya serializables
    }

    # 3. Persistir en historial.json (append, no sobrescribir)
    _guardar_entrada(entrada)

    print(entrada)

    # 4. ── TELEGRAM ───────────────────────────────────────────────────────────
    # Aquí va la llamada al servicio de Telegram.
    # Se debe importar el módulo del bot y llamar algo como:
    #
    #   from app.services.telegram import enviar_diagnostico
    #   telegram_ok = enviar_diagnostico(entrada)
    #
    # El mensaje a Telegram debe incluir:
    #   - Usuario
    #   - Síntomas seleccionados (nombres, no IDs)
    #   - Para cada diagnóstico: falla_id, nombre, tipo, descripcion
    #   - Lista de recomendaciones
    #   - Fecha y historial_id
    #
    # Si no hay diagnósticos, se puede omitir la notificación o enviar
    # un mensaje de "sin resultados". 
    # ─────────────────────────────────────────────────────────────────────────
    telegram_ok = False

    if mensaje:
        telegram_ok = enviar_diagnostico(entrada)

    return {
        "diagnosticos": diagnosticos,
        "historial_id": historial_id,
        "telegram_enviado": telegram_ok,
        # Si la lista está vacía, el controller agrega el campo "mensaje"
    }


# ── Servicio: listar síntomas ─────────────────────────────────────────────────

def obtener_sintomas() -> list[dict]:
    """
    Retorna todos los síntomas disponibles desde Prolog.
    El controller los envuelve en {"sintomas": [...]}
    """
    return prolog.listar_sintomas()


# ── Servicio: historial ───────────────────────────────────────────────────────

def obtener_historial(limit: int = 20, offset: int = 0) -> dict:
    """
    Lee historial.json, ordena de más reciente a más antiguo,
    aplica paginación y retorna total + página.

    Args:
        limit:  Máximo de entradas a retornar.
        offset: Cuántas entradas saltar (para paginación).

    Returns:
        {"total": int, "historial": [...]}
    """
    historial = _leer_historial()

    # Más reciente primero
    historial_ordenado = sorted(historial, key=lambda e: e["fecha"], reverse=True)

    total = len(historial_ordenado)
    pagina = historial_ordenado[offset: offset + limit]

    return {"total": total, "historial": pagina}


def obtener_entrada_historial(id_: str) -> dict | None:
    """
    Busca una entrada específica del historial por su UUID.

    Returns:
        El dict de la entrada o None si no existe.
    """
    historial = _leer_historial()
    for entrada in historial:
        if entrada.get("id") == id_:
            return entrada
    return None