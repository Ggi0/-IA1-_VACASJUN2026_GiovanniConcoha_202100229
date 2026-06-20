"""
rpa_service.py
==============
Wrapper del bot RPA. Este es el archivo que invoice_service llama
directamente. Se encarga de:

    1. Lanzar el bot Selenium (RPABot)
    2. Esperar el resultado
    3. Guardar la factura en la DB (vía invoice_repository)
    4. Registrar la bitácora (vía log_service)

invoice_service NUNCA llama a rpa_bot.py directamente.
Siempre va a través de este archivo.

Arquitectura de llamadas:
    invoice_controller
        └─► invoice_service.process_invoice()
                └─► rpa_service.execute_rpa_and_save()   ← ESTE ARCHIVO
                        ├─► RPABot.fill_and_submit()
                        ├─► invoice_repository.create()
                        └─► log_service.create_log()
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.rpa.rpa_bot import RPABot, RPABotResult

logger = logging.getLogger(__name__)

# ThreadPoolExecutor para correr Selenium (síncrono) sin bloquear el event loop de FastAPI
_rpa_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="rpa_worker")


class RPAService:
    """
    Servicio RPA que coordina el bot, el guardado en DB y la bitácora.

    Uso desde invoice_service:
        rpa_service = RPAService()
        result = await rpa_service.execute_rpa_and_save(
            invoice_data=ocr_result_dict,
            file_path="/app/uploads/abc123.pdf",
            user_id=1,
            db=db,
        )
    """

    # ─────────────────────────────────────────────────────────────────
    # MÉTODO PRINCIPAL — llamado por invoice_service
    # ─────────────────────────────────────────────────────────────────

    async def execute_rpa_and_save(
        self,
        invoice_data: dict,
        file_path: str,
        user_id: int,
        db: AsyncSession,
    ) -> dict:
        """
        Flujo completo post-OCR:
            1. Corre el bot Selenium en un thread separado
            2. Si el bot tiene éxito → guarda la factura en DB con status PROCESSED
            3. Si el bot falla → guarda con status ERROR
            4. Registra la bitácora en ambos casos

        Args:
            invoice_data: dict con los campos validados de la factura.
                          Debe tener: invoice_number, date, provider,
                          nit, subtotal, taxes, total.
            file_path:    Ruta donde está guardado el archivo.
            user_id:      ID del usuario autenticado.
            db:           Sesión de base de datos AsyncSession.

        Returns:
            dict con:
                success         → bool
                invoice_id      → int (ID en DB) | None
                rpa_status      → "SUCCESS" | "FAILED"
                rpa_message     → str (mensaje del frontend o error)
                duration_ms     → float
        """
        logger.info(f"RPAService: Iniciando flujo RPA para factura '{invoice_data.get('invoice_number')}'")

        # ── Paso 1: Ejecutar el bot en un thread (Selenium es síncrono) ──
        rpa_result: RPABotResult = await self._run_bot_in_thread(
            invoice_data=invoice_data,
            file_path=file_path,
            user_id=user_id,
        )

        logger.info(
            f"RPAService: Bot terminó | success={rpa_result.success} | "
            f"mensaje='{rpa_result.message}' | tiempo={rpa_result.duration_ms}ms"
        )

        # ── Paso 2: Guardar factura en la DB ──────────────────────────
        invoice_id = await self._save_invoice_to_db(
            invoice_data=invoice_data,
            file_path=file_path,
            user_id=user_id,
            rpa_result=rpa_result,
            db=db,
        )

        # ── Paso 3: Registrar bitácora ────────────────────────────────
        await self._write_log(
            invoice_id=invoice_id,
            user_id=user_id,
            rpa_result=rpa_result,
            db=db,
        )

        return {
            "success":     rpa_result.success,
            "invoice_id":  invoice_id,
            "rpa_status":  "SUCCESS" if rpa_result.success else "FAILED",
            "rpa_message": rpa_result.message,
            "duration_ms": rpa_result.duration_ms,
        }

    # ─────────────────────────────────────────────────────────────────
    # Ejecutar bot en thread separado (no bloquea FastAPI)
    # ─────────────────────────────────────────────────────────────────

    async def _run_bot_in_thread(
        self,
        invoice_data: dict,
        file_path: str,
        user_id: int,
    ) -> RPABotResult:
        """
        Selenium corre de forma síncrona. Para no bloquear el event loop
        de FastAPI lo corremos en un ThreadPoolExecutor.

        asyncio.get_event_loop().run_in_executor() delega la función
        síncrona al thread pool y la awaita desde el código async.
        """
        loop = asyncio.get_event_loop()

        def _run_sync():
            """Esta función síncrona corre en el thread pool."""
            with RPABot() as bot:
                return bot.fill_and_submit(
                    invoice_data=invoice_data,
                    file_path=file_path,
                    user_id=user_id,
                )

        try:
            result = await loop.run_in_executor(_rpa_executor, _run_sync)
            return result
        except Exception as e:
            logger.error(f"RPAService: Error en thread del bot: {e}", exc_info=True)
            return RPABotResult(
                success=False,
                message=f"Error lanzando el bot: {str(e)}",
                error_type="THREAD_ERROR",
            )

    # ─────────────────────────────────────────────────────────────────
    # Guardar factura en DB
    # ─────────────────────────────────────────────────────────────────

    async def _save_invoice_to_db(
        self,
        invoice_data: dict,
        file_path: str,
        user_id: int,
        rpa_result: RPABotResult,
        db: AsyncSession,
    ) -> Optional[int]:
        """
        Guarda la factura en la tabla `invoices`.
        El status depende del resultado del RPA:
            RPA exitoso  → PROCESSED
            RPA fallido  → ERROR
        """
        from app.repositories.invoice_repository import InvoiceRepository
        from app.repositories.provider_repository import ProviderRepository

        try:
            provider_repo = ProviderRepository()
            invoice_repo = InvoiceRepository()

            # Buscar o crear proveedor por NIT
            provider = provider_repo.get_or_create_by_nit(
                db,
                nit=invoice_data.get("nit", "CF"),
                name=invoice_data.get("provider", "Desconocido"),
            )

            # Determinar status según resultado del RPA
            status = "PROCESSED" if rpa_result.success else "ERROR"

            invoice = invoice_repo.create(
                db,
                {
                    "user_id": user_id,
                    "provider_id": provider.id,
                    "invoice_number": invoice_data.get("invoice_number"),
                    "date": invoice_data.get("date"),
                    "nit": invoice_data.get("nit"),
                    "subtotal": float(invoice_data.get("subtotal") or 0),
                    "taxes": float(invoice_data.get("taxes") or 0),
                    "total": float(invoice_data.get("total") or 0),
                    "file_path": file_path,
                    "status": status,
                }
            )

            invoice_id = invoice.id

            logger.info(f"RPAService: Factura guardada en DB con ID={invoice_id}, status={status}")
            return invoice_id

        except Exception as e:
            logger.error(f"RPAService: Error guardando factura en DB: {e}", exc_info=True)
            return None

    # ─────────────────────────────────────────────────────────────────
    # Escribir bitácora
    # ─────────────────────────────────────────────────────────────────

    async def _write_log(
        self,
        invoice_id: Optional[int],
        user_id: int,
        rpa_result: RPABotResult,
        db: AsyncSession,
    ):
        """
        Registra en la tabla `process_logs` el resultado del proceso completo.

        Campos que escribe:
            invoice_id    → FK a la factura recién guardada
            user_id       → quien procesó
            status        → PROCESSED o ERROR (refleja el RPA)
            rpa_result    → SUCCESS o FAILED
            message       → mensaje del bot o descripción del error
        """
        from app.repositories.log_repository import LogRepository

        try:
            log_repo = LogRepository()
            log_repo.create_log(
                db,
                invoice_id=invoice_id,
                user_id=user_id,
                status="PROCESSED" if rpa_result.success else "ERROR",
                rpa_result="SUCCESS" if rpa_result.success else "FAILED",
                message=rpa_result.message or "Sin mensaje",
            )
            logger.info(f"RPAService: Bitácora registrada para invoice_id={invoice_id}")
        except Exception as e:
            logger.error(f"RPAService: Error escribiendo bitácora: {e}", exc_info=True)