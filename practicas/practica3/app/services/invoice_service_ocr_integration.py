"""
invoice_service.py  (fragmento de integración OCR)
===================================================
Este archivo muestra EXACTAMENTE cómo invoice_service.py
debe consumir el pipeline OCR.

En tu proyecto, integra estos métodos dentro de tu InvoiceService existente.
"""

import logging
import os
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ocr.ocr_pipeline import get_ocr_pipeline, OCRResult

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_MB = 10


class InvoiceService:

    # ─────────────────────────────────────────────────────────────────
    # PASO 1 + 2 + 3: Recibir archivo, guardar, y ejecutar OCR
    # ─────────────────────────────────────────────────────────────────

    async def upload_and_extract(
        self,
        file: UploadFile,
        user_id: int,
        db: AsyncSession,
    ) -> dict:
        """
        Punto de entrada principal del flujo de factura.

        Llamado desde:
            POST /invoices/upload

        Retorna:
            dict con los campos extraídos y el estado de validación.
            Si success=True → todo OK, procede al RPA.
            Si success=False → devolver al frontend para edición manual.
        """

        # ── Validar extensión ───────────────────────────────────────
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato no soportado: '{ext}'. Usa PDF, JPG, JPEG o PNG."
            )

        # ── Leer bytes del archivo ──────────────────────────────────
        file_bytes = await file.read()

        if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"Archivo demasiado grande. Máximo {MAX_FILE_SIZE_MB}MB."
            )

        # ── Guardar archivo en disco ────────────────────────────────
        saved_filename = f"{uuid.uuid4()}{ext}"
        saved_path = UPLOAD_DIR / saved_filename
        saved_path.write_bytes(file_bytes)
        logger.info(f"Archivo guardado: {saved_path}")

        # ── Ejecutar pipeline OCR ───────────────────────────────────
        pipeline = get_ocr_pipeline(engine="auto")
        ocr_result: OCRResult = await pipeline.process_bytes(file_bytes, file.filename)

        logger.info(
            f"OCR completado | éxito={ocr_result.success} | "
            f"campos={ocr_result.confidence} | "
            f"tiempo={ocr_result.processing_time_ms}ms"
        )

        if not ocr_result.success:
            # Error técnico en el OCR (no en la extracción, sino en el proceso)
            return {
                "status": "ERROR",
                "message": f"Error en OCR: {ocr_result.error_message}",
                "file_path": str(saved_path),
                "extracted_data": None,
            }

        # ── Preparar respuesta para el frontend ─────────────────────
        extracted = {
            "invoice_number": ocr_result.invoice_number,
            "date":           ocr_result.date,
            "provider":       ocr_result.provider,
            "nit":            ocr_result.nit,
            "subtotal":       ocr_result.subtotal,
            "taxes":          ocr_result.taxes,
            "total":          ocr_result.total,
        }

        missing = ocr_result.missing_fields()

        return {
            # El frontend usa este status para decidir si muestra
            # el formulario de edición o continúa al RPA
            "status": "NEEDS_REVIEW" if missing else "READY",
            "missing_fields": missing,
            "extracted_data": extracted,
            "confidence": ocr_result.confidence,
            "raw_text": ocr_result.raw_text,
            "file_path": str(saved_path),
            "processing_time_ms": ocr_result.processing_time_ms,
        }

    # ─────────────────────────────────────────────────────────────────
    # PASO POSTERIOR: Guardar en DB después de validación
    # ─────────────────────────────────────────────────────────────────

    async def save_invoice(
        self,
        extracted_data: dict,
        file_path: str,
        user_id: int,
        db: AsyncSession,
    ) -> int:
        """
        Guarda la factura en la base de datos.

        Llamado después de que:
            a) La validación automática pasó sin errores, O
            b) El empleado corrigió manualmente los datos.

        Args:
            extracted_data: dict con los campos (puede venir del OCR o del form editado).
            file_path:      Ruta donde se guardó el archivo.
            user_id:        ID del usuario que procesó la factura.
            db:             Sesión de base de datos.

        Returns:
            int: ID de la factura guardada.
        """
        from app.repositories.invoice_repository import InvoiceRepository
        from app.repositories.provider_repository import ProviderRepository

        repo = InvoiceRepository(db)
        provider_repo = ProviderRepository(db)

        # Buscar o crear proveedor por NIT
        provider = await provider_repo.get_or_create_by_nit(
            nit=extracted_data["nit"],
            name=extracted_data.get("provider", "Desconocido"),
        )

        invoice_id = await repo.create(
            user_id=user_id,
            provider_id=provider.id,
            invoice_number=extracted_data["invoice_number"],
            date=extracted_data["date"],
            nit=extracted_data["nit"],
            subtotal=extracted_data["subtotal"],
            taxes=extracted_data["taxes"],
            total=extracted_data["total"],
            file_path=file_path,
            status="PENDING",  # El RPA lo cambiará a PROCESSED
        )

        logger.info(f"Factura guardada con ID: {invoice_id}")
        return invoice_id