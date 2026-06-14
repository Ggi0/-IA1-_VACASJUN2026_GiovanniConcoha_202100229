import os
import requests

from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


class TelegramService:

    @staticmethod
    def get_updates(offset: int = None, timeout: int = 30):
        """
        Long polling: obtiene mensajes nuevos del bot.
        """
        params = {
            "timeout": timeout
        }

        if offset is not None:
            params["offset"] = offset

        try:
            response = requests.get(
                f"{TELEGRAM_API_URL}/getUpdates",
                params=params,
                timeout=timeout + 10
            )

            return response.json()

        except Exception as e:
            print("[TELEGRAM] Error en get_updates:", e)
            return {"ok": False, "result": []}

    @staticmethod
    def enviar_mensaje(chat_id: int, texto: str) -> bool:
        """
        Envía un mensaje de texto a un chat específico.
        """
        try:
            if not TELEGRAM_TOKEN:
                print("[TELEGRAM] Token no configurado.")
                return False

            url = f"{TELEGRAM_API_URL}/sendMessage"

            payload = {
                "chat_id": chat_id,
                "text": texto,
                "parse_mode": "HTML",
            }

            response = requests.post(
                url,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return True

            print("[TELEGRAM] Error sendMessage:", response.text)
            return False

        except Exception as e:
            print("[TELEGRAM] Error enviando mensaje:", e)
            return False