"""
invoice_service.py
==================
Orquestador principal del flujo de factura.
Este archivo reemplaza a invoice_service_ocr_integration.py.

Responsabilidades:
    1. Recibir el archivo → OCR → extraer datos
    2. Validar los datos extraídos
    3. Coordinar el RPA (via rpa_service)
    4. Consultas de facturas

Consume:
    - OCRPipeline          (módulo ocr)
    - ValidationService    (services)
    - RPAService           (módulo rpa)
    - InvoiceRepository    (repositories)
    - ProviderRepository   (repositories)
    - LogRepository        (repositories)

Es consumido por: invoice_controller.py

NOTA SOBRE SYNC vs ASYNC:
    La base de datos usa Session síncrona (SQLAlchemy sync).
    El OCR usa await (async).
    Resolvemos esto: los métodos del service son async cuando
    llaman al OCR o al RPA, y usan session síncrona normalmente.
"""

import os
import uuid
import logging
from pathlib import Path

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.modules.ocr.ocr_pipeline import get_ocr_pipeline, OCRResult
from app.services.validation_service import ValidationService
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.provider_repository import ProviderRepository
from app.repositories.log_repository import LogRepository

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent  # apunta a app/
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))


class InvoiceService:

    def __init__(self):
        self.validation_service  = ValidationService()
        self.invoice_repo        = InvoiceRepository()
        self.provider_repo       = ProviderRepository()
        self.log_repo            = LogRepository()

    # ═══════════════════════════════════════════════════════════════
    # PASO 2 + 3 + 4 + 5: Upload → OCR → Extracción → Validación
    # Llamado desde: POST /invoices/upload
    # ═══════════════════════════════════════════════════════════════

    async def upload_and_process(
        self,
        file: UploadFile,
        user_id: int,
        db: Session,
    ) -> dict:
        """
        Recibe el archivo del empleado, corre el OCR y valida los datos.

        Retorna al frontend uno de tres estados:
            READY        → Todos los campos OK, el frontend llama a /trigger-rpa
            NEEDS_REVIEW → Hay campos faltantes o con errores de validación,
                           el frontend muestra el form editable
            ERROR        → Fallo técnico del OCR (archivo corrompido, etc.)

        Args:
            file:    UploadFile de FastAPI (PDF, JPG, JPEG, PNG).
            user_id: ID del usuario autenticado.
            db:      Sesión de base de datos.

        Returns:
            dict con status, extracted_data, validation, file_path.
        """
        # ── Validar extensión ───────────────────────────────────
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato '{ext}' no soportado. Usa PDF, JPG, JPEG o PNG."
            )

        # ── Leer bytes ──────────────────────────────────────────
        file_bytes = await file.read()

        if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"Archivo demasiado grande. Máximo {MAX_FILE_SIZE_MB}MB."
            )

        # ── Guardar en disco ────────────────────────────────────
        saved_filename = f"{uuid.uuid4()}{ext}"
        saved_path = UPLOAD_DIR / saved_filename
        saved_path.write_bytes(file_bytes)
        logger.info(f"Archivo guardado: {saved_path}")

        # ── OCR ─────────────────────────────────────────────────
        pipeline = get_ocr_pipeline(engine="auto")
        ocr_result: OCRResult = await pipeline.process_bytes(file_bytes, file.filename)

        logger.info(
            f"OCR completado | success={ocr_result.success} | "
            f"tiempo={ocr_result.processing_time_ms}ms | "
            f"motor={ocr_result.engine_used}"
        )

        if not ocr_result.success:
            # Error técnico: archivo no legible, Tesseract crasheó, etc.
            return {
                "status":         "ERROR",
                "message":        f"Error procesando el archivo: {ocr_result.error_message}",
                "file_path":      str(saved_path),
                "extracted_data": None,
                "validation":     None,
            }

        # ── Datos extraídos por el OCR ──────────────────────────
        extracted = {
            "invoice_number": ocr_result.invoice_number,
            "date":           ocr_result.date,
            "provider":       ocr_result.provider,
            "nit":            ocr_result.nit,
            "subtotal":       ocr_result.subtotal,
            "taxes":          ocr_result.taxes,
            "total":          ocr_result.total,
        }

        # ── Validación ──────────────────────────────────────────
        # Pasamos la DB para que también verifique duplicados
        validation = self.validation_service.validate(extracted, db=db)

        if not validation.is_valid:
            logger.warning(
                f"Validación FALLIDA para '{file.filename}': "
                f"{[e.field for e in validation.errors]}"
            )
            return {
                "status":         "NEEDS_REVIEW",
                "message":        "Algunos campos requieren revisión o corrección.",
                "file_path":      str(saved_path),
                "extracted_data": extracted,
                "validation": {
                    "is_valid": False,
                    "errors":   [{"field": e.field, "message": e.message}
                                 for e in validation.errors],
                    "warnings": validation.warnings,
                },
                "confidence":         ocr_result.confidence,
                "raw_text":           ocr_result.raw_text,
                "processing_time_ms": ocr_result.processing_time_ms,
            }

        logger.info(f"Validación OK para '{file.filename}'")

        return {
            "status":         "READY",
            "message":        "Factura procesada y validada. Lista para registrar.",
            "file_path":      str(saved_path),
            "extracted_data": validation.clean_data,  # Datos normalizados
            "validation": {
                "is_valid": True,
                "errors":   [],
                "warnings": validation.warnings,
            },
            "confidence":         ocr_result.confidence,
            "raw_text":           ocr_result.raw_text,
            "processing_time_ms": ocr_result.processing_time_ms,
        }

    # ═══════════════════════════════════════════════════════════════
    # PASO 5b: Validar datos corregidos manualmente por el empleado
    # Llamado desde: POST /invoices/validate
    # ═══════════════════════════════════════════════════════════════

    def validate_manual(self, data: dict, db: Session) -> dict:
        """
        El empleado corrigió los datos en el formulario editable.
        Este método valida los datos corregidos antes de enviarlos al RPA.

        Args:
            data: dict con los campos corregidos por el empleado.
            db:   Sesión de base de datos.

        Returns:
            dict con is_valid, errors, warnings y clean_data.
        """
        validation = self.validation_service.validate(data, db=db)
        return validation.to_dict()

    # ═══════════════════════════════════════════════════════════════
    # PASO 6 + 7 + 8: Disparar RPA → Guardar → Bitácora
    # Llamado desde: POST /invoices/trigger-rpa
    # ═══════════════════════════════════════════════════════════════

    async def trigger_rpa_flow(
        self,
        invoice_data: dict,
        file_path: str,
        user_id: int,
        db: Session,
    ) -> dict:
        """
        Lanza el bot RPA con los datos validados.
        El RPA llena el formulario /rpa-form, lo envía y el endpoint
        /rpa-submit guarda en la DB y crea la bitácora.

        Si el RPA falla, de todas formas guarda la factura con status=ERROR.

        Args:
            invoice_data: dict con los campos validados de la factura.
            file_path:    Ruta del archivo en disco.
            user_id:      ID del usuario autenticado.
            db:           Sesión de base de datos.

        Returns:
            dict con success, invoice_id, rpa_status, rpa_message.
        """
        # Validar una última vez antes de lanzar el RPA
        validation = self.validation_service.validate(invoice_data)
        if not validation.is_valid:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Los datos no pasaron la validación final.",
                    "errors":  [{"field": e.field, "message": e.message}
                                for e in validation.errors],
                }
            )

        # Lanzar el RPA
        from app.modules.rpa.rpa_service import RPAService
        rpa_service = RPAService()

        result = await rpa_service.execute_rpa_and_save(
            invoice_data=validation.clean_data,
            file_path=file_path,
            user_id=user_id,
            db=db,
        )

        return result

    # ═══════════════════════════════════════════════════════════════
    # ENDPOINT /invoices/rpa-submit
    # Llamado INTERNAMENTE por el formulario React (no por el empleado)
    # ═══════════════════════════════════════════════════════════════

    def rpa_submit(
        self,
        payload: dict,
        db: Session,
    ) -> dict:

        # 🔥 Obtener token desde payload
        rpa_token = payload.get("rpa_token")

        expected_token = os.getenv("RPA_SECRET_TOKEN", "smartinvoice-rpa-secret-2024")

        if rpa_token != expected_token:
            logger.warning("rpa-submit: Token inválido.")
            raise HTTPException(status_code=403, detail="Token RPA inválido.")

        # Buscar o crear proveedor
        provider = self.provider_repo.get_or_create_by_nit(
            db=db,
            nit=payload.get("nit", "CF"),
            name=payload.get("provider", "Desconocido"),
        )

        invoice_data = {
            "user_id":        int(payload.get("user_id") or 1),
            "provider_id":    provider.id,
            "invoice_number": payload.get("invoice_number"),
            "date":           payload.get("date"),
            "nit":            payload.get("nit"),
            "subtotal":       float(payload.get("subtotal") or 0),
            "taxes":          float(payload.get("taxes") or 0),
            "total":          float(payload.get("total") or 0),
            "file_path":      payload.get("file_path", ""),
            "status":         "PROCESSED",
            "is_duplicate":   False,
        }

        existing = self.invoice_repo.find_duplicate(
            db,
            invoice_data["invoice_number"],
            invoice_data["nit"]
        )

        if existing:
            invoice_data["is_duplicate"] = True

        invoice = self.invoice_repo.create(db, invoice_data)

        self.log_repo.create_log(
            db=db,
            invoice_id=invoice.id,
            user_id=invoice_data["user_id"],
            status="PROCESSED",
            rpa_result="SUCCESS",
            message="Factura registrada mediante automatización RPA.",
        )

        logger.info(f"rpa-submit: Factura guardada ID={invoice.id}")

        return {
            "status":     "ok",
            "invoice_id": invoice.id,
            "message":    f"Factura procesada correctamente. ID: {invoice.id}",
        }
    # ═══════════════════════════════════════════════════════════════
    # CONSULTAS
    # ═══════════════════════════════════════════════════════════════

    def get_all(self, db: Session) -> list:
        """Retorna todas las facturas."""
        invoices = self.invoice_repo.get_all(db)
        return [self._serialize(inv) for inv in invoices]

    def get_by_id(self, db: Session, invoice_id: int) -> dict:
        """Retorna una factura por ID."""
        invoice = self.invoice_repo.get_by_id(db, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail=f"Factura ID {invoice_id} no encontrada.")
        return self._serialize(invoice)

    def get_logs(self, db: Session, invoice_id: int) -> list:
        """Retorna la bitácora de una factura."""
        invoice = self.invoice_repo.get_by_id(db, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail=f"Factura ID {invoice_id} no encontrada.")
        logs = self.log_repo.get_logs_by_invoice(db, invoice_id)
        return [self._serialize_log(log) for log in logs]

    # ─────────────────────────────────────────────────────────────
    # Serialización
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _serialize(invoice) -> dict:
        return {
            "id":             invoice.id,
            "invoice_number": invoice.invoice_number,
            "date":           str(invoice.date) if invoice.date else None,
            "nit":            invoice.nit,
            "subtotal":       float(invoice.subtotal) if invoice.subtotal else None,
            "taxes":          float(invoice.taxes)    if invoice.taxes    else None,
            "total":          float(invoice.total)    if invoice.total    else None,
            "status":         invoice.status.value    if invoice.status   else None,
            "is_duplicate":   invoice.is_duplicate,
            "file_path":      invoice.file_path,
            "provider_id":    invoice.provider_id,
            "user_id":        invoice.user_id,
            "created_at":     str(invoice.created_at) if invoice.created_at else None,
        }

    @staticmethod
    def _serialize_log(log) -> dict:
        return {
            "id":           log.id,
            "invoice_id":   log.invoice_id,
            "user_id":      log.user_id,
            "process_date": str(log.process_date) if log.process_date else None,
            "status":       log.status.value    if log.status    else None,
            "rpa_result":   log.rpa_result.value if log.rpa_result else None,
            "message":      log.message,
        }