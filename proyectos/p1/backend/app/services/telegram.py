# app/services/telegram.py

import os
import requests

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def _construir_mensaje(entrada: dict) -> str:
    """
    Construye un mensaje HTML amigable para Telegram.
    """

    historial_id = entrada["id"]
    fecha = entrada["fecha"]
    usuario = entrada["usuario"]
    sintomas = entrada["sintomas_seleccionados"]
    diagnosticos = entrada["diagnosticos"]

    mensaje = (
        "🩺 <b>NUEVO DIAGNÓSTICO - DOCTOR BYTE</b>\n\n"
        f"👤 <b>Usuario:</b> {usuario}\n"
        f"📅 <b>Fecha:</b> {fecha}\n"
        f"🆔 <b>ID:</b> <code>{historial_id}</code>\n\n"
    )

    # Síntomas seleccionados
    mensaje += "🔍 <b>Síntomas seleccionados</b>\n"

    for sintoma in sintomas:
        mensaje += f"• {sintoma}\n"

    mensaje += "\n"

    # Sin diagnósticos
    if not diagnosticos:
        mensaje += (
            "⚠️ <b>Resultado</b>\n"
            "No se encontró ninguna falla compatible con los síntomas proporcionados.\n"
        )
        return mensaje

    # Diagnósticos encontrados
    mensaje += f"✅ <b>Diagnósticos encontrados ({len(diagnosticos)})</b>\n\n"

    for i, diagnostico in enumerate(diagnosticos, start=1):

        mensaje += (
            f"━━━━━━━━━━━━━━\n"
            f"🔧 <b>Diagnóstico #{i}</b>\n\n"
            f"🆔 <b>Falla:</b> {diagnostico['falla_id']}\n"
            f"📌 <b>Nombre:</b> {diagnostico['nombre']}\n"
            f"🏷️ <b>Tipo:</b> {diagnostico['tipo']}\n\n"
            f"📖 <b>Descripción</b>\n"
            f"{diagnostico['descripcion']}\n\n"
        )

        recomendaciones = diagnostico.get("recomendaciones", [])

        if recomendaciones:
            mensaje += "💡 <b>Recomendaciones</b>\n"

            for idx, recomendacion in enumerate(recomendaciones, start=1):
                mensaje += f"{idx}. {recomendacion}\n"

            mensaje += "\n"

    return mensaje


def enviar_diagnostico(entrada: dict) -> bool:
    """
    Envía el diagnóstico al grupo/canal/chat configurado.
    """

    try:

        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            print("Telegram no configurado.")
            return False

        mensaje = _construir_mensaje(entrada)

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje,
            "parse_mode": "HTML",
        }

        response = requests.post(
            url,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            return True

        print("Error Telegram:", response.text)
        return False

    except Exception as e:
        print("Error enviando Telegram:", e)
        return False