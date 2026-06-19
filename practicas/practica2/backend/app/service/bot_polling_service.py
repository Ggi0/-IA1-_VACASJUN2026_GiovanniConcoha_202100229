import threading
import time

from app.service.telegram_service import TelegramService
from app.service.bot_service import BotService


class BotPollingService:

    _thread = None
    _running = False
    _offset = None

    @classmethod
    def iniciar(cls):
        if cls._running:
            return

        cls._running = True

        cls._thread = threading.Thread(
            target=cls._loop,
            daemon=True
        )

        cls._thread.start()

        print("[BOT] Polling iniciado.")

    @classmethod
    def detener(cls):
        cls._running = False

    @classmethod
    def _loop(cls):
        while cls._running:

            try:
                data = TelegramService.get_updates(
                    offset=cls._offset,
                    timeout=30
                )

                if not data.get("ok"):
                    time.sleep(2)
                    continue

                resultados = data.get("result", [])

                for update in resultados:

                    update_id = update.get("update_id")

                    if update_id is not None:
                        cls._offset = update_id + 1

                    try:
                        BotService.procesar_update(update)
                    except Exception as e:
                        print("[BOT] Error procesando update:", e)

            except Exception as e:
                print("[BOT] Error en loop de polling:", e)
                time.sleep(3)