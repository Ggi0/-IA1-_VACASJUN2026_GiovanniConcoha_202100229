from sqlalchemy.orm import Session

from app.config.db import SessionLocal
from app.repositories.pregunta_repository import PreguntaRepository
from app.repositories.telegram_chat_repository import TelegramChatRepository
from app.repositories.consulta_repository import ConsultaRepository
from app.service.telegram_service import TelegramService


class BotService:

    MENSAJE_AYUDA = (
        "🤖 <b>SmartBot - Ayuda</b>\n\n"
        "Comandos disponibles:\n"
        "• /id - Muestra el ID de este chat\n"
        "• /saludar - Te saluda el bot\n"
        "• /help - Muestra este mensaje de ayuda\n\n"
        "También puedes escribirme una pregunta y buscaré "
        "una respuesta en mi base de conocimiento."
    )

    MENSAJE_SALUDO = (
        "👋 ¡Hola! Soy <b>SmartBot</b>.\n"
        "Estoy aquí para responder tus preguntas frecuentes.\n"
        "Escribe /help para ver los comandos disponibles."
    )

    MENSAJE_NO_AUTORIZADO = (
        "🚫 Este chat no está autorizado para usar el bot.\n\n"
        "Pide a un administrador que registre este chat con el "
        "siguiente ID:\n"
        "<code>{chat_id}</code>"
    )

    MENSAJE_SIN_RESPUESTA = (
        "🤔 No encontré una respuesta para tu consulta.\n"
        "Intenta usar otras palabras o escribe /help."
    )

    # ------------------------------------------------------------------
    # Punto de entrada principal
    # ------------------------------------------------------------------

    @classmethod
    def procesar_update(cls, update: dict):
        mensaje = update.get("message")

        if not mensaje:
            return

        chat = mensaje.get("chat", {})
        chat_id = chat.get("id")
        texto = mensaje.get("text", "")

        if chat_id is None or not texto:
            return

        texto = texto.strip()

        db = SessionLocal()

        try:
            # /id siempre responde, sin importar autorización
            if texto.startswith("/id"):
                cls._comando_id(chat_id)
                return

            autorizado = cls._chat_autorizado(db, chat_id)

            if not autorizado:
                TelegramService.enviar_mensaje(
                    chat_id,
                    cls.MENSAJE_NO_AUTORIZADO.format(chat_id=chat_id)
                )
                return

            if texto.startswith("/help"):
                cls._comando_help(chat_id)
                return

            if texto.startswith("/saludar"):
                cls._comando_saludar(chat_id)
                return

            if texto.startswith("/"):
                TelegramService.enviar_mensaje(
                    chat_id,
                    "❓ Comando no reconocido. Escribe /help para ver opciones."
                )
                return

            # Cualquier otro texto -> buscar respuesta en BD
            cls._responder_pregunta(db, chat_id, texto)

        finally:
            db.close()

    # ------------------------------------------------------------------
    # Comandos
    # ------------------------------------------------------------------

    @classmethod
    def _comando_id(cls, chat_id: int):
        texto = (
            "🆔 <b>ID de este chat</b>\n\n"
            f"<code>{chat_id}</code>\n\n"
            "Comparte este ID con el administrador para que "
            "autorice este chat."
        )

        TelegramService.enviar_mensaje(chat_id, texto)

    @classmethod
    def _comando_help(cls, chat_id: int):
        TelegramService.enviar_mensaje(chat_id, cls.MENSAJE_AYUDA)

    @classmethod
    def _comando_saludar(cls, chat_id: int):
        TelegramService.enviar_mensaje(chat_id, cls.MENSAJE_SALUDO)

    # ------------------------------------------------------------------
    # Autorización
    # ------------------------------------------------------------------

    @staticmethod
    def _chat_autorizado(db: Session, chat_id: int) -> bool:
        registro = TelegramChatRepository.obtener_por_chat_id(
            db,
            chat_id
        )

        if not registro:
            return False

        return registro.activo is True

    # ------------------------------------------------------------------
    # Búsqueda de respuestas
    # ------------------------------------------------------------------

    @classmethod
    def _responder_pregunta(cls, db: Session, chat_id: int, texto: str):
        coincidencias = PreguntaRepository.buscar_por_palabra_clave(db, texto)

        if not coincidencias:
            ConsultaRepository.registrar(
                db,
                chat_id=chat_id,
                pregunta=texto,
                respuesta=None
            )

            TelegramService.enviar_mensaje(
                chat_id,
                cls.MENSAJE_SIN_RESPUESTA
            )
            return

        mejor = coincidencias[0]

        respuesta_texto = (
            f"💬 <b>{mejor.pregunta}</b>\n\n"
            f"{mejor.respuesta}"
        )

        ConsultaRepository.registrar(
            db,
            chat_id=chat_id,
            pregunta=texto,
            respuesta=mejor.respuesta
        )

        TelegramService.enviar_mensaje(chat_id, respuesta_texto)