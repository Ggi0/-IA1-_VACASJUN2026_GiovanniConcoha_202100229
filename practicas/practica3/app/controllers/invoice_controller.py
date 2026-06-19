"""
invoice_controller.py  — fragmento del endpoint RPA
====================================================
Este archivo muestra los dos endpoints que el flujo RPA necesita.

Integra estos dos routers en tu invoice_controller.py existente.

Endpoints:
    POST /invoices/upload           ← Recibe el archivo, corre OCR
    POST /invoices/rpa-submit       ← Recibe el submit del formulario React (del bot)
    POST /invoices/{id}/trigger-rpa ← invoice_service dispara el RPA manualmente
                                       (cuando el empleado corrigió datos y aprueba)
"""

import os
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.ocr.ocr_pipeline import get_ocr_pipeline
from app.modules.rpa.rpa_service import RPAService
from app.schemas.invoice_schema import RPASubmitPayload

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/invoices", tags=["Invoices"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
RPA_SECRET_TOKEN = os.getenv("RPA_SECRET_TOKEN", "smartinvoice-rpa-secret-2024")


# ─────────────────────────────────────────────────────────────────
# POST /invoices/upload — Paso 1: OCR
# ─────────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_invoice(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Recibe el archivo de factura, lo procesa con OCR y devuelve
    los datos extraídos al frontend.

    El frontend decide:
        status=READY        → llama a /invoices/{tmp_id}/trigger-rpa
        status=NEEDS_REVIEW → muestra formulario editable al empleado
    """
    import uuid
    from app.modules.ocr.ocr_pipeline import OCRResult

    ext = Path(file.filename).suffix.lower()
    allowed = {".pdf", ".jpg", ".jpeg", ".png"}
    if ext not in allowed:
        raise HTTPException(400, f"Formato no soportado: {ext}")

    file_bytes = await file.read()

    # Guardar archivo
    saved_filename = f"{uuid.uuid4()}{ext}"
    saved_path = UPLOAD_DIR / saved_filename
    saved_path.write_bytes(file_bytes)

    # OCR
    pipeline = get_ocr_pipeline()
    ocr_result: OCRResult = await pipeline.process_bytes(file_bytes, file.filename)

    if not ocr_result.success:
        return {
            "status": "ERROR",
            "message": ocr_result.error_message,
            "file_path": str(saved_path),
        }

    missing = ocr_result.missing_fields()
    extracted = {
        "invoice_number": ocr_result.invoice_number,
        "date":           ocr_result.date,
        "provider":       ocr_result.provider,
        "nit":            ocr_result.nit,
        "subtotal":       ocr_result.subtotal,
        "taxes":          ocr_result.taxes,
        "total":          ocr_result.total,
    }

    return {
        "status":         "NEEDS_REVIEW" if missing else "READY",
        "missing_fields": missing,
        "extracted_data": extracted,
        "confidence":     ocr_result.confidence,
        "file_path":      str(saved_path),
        "raw_text":       ocr_result.raw_text,
    }


# ─────────────────────────────────────────────────────────────────
# POST /invoices/trigger-rpa — Paso 2: El frontend dispara el RPA
# ─────────────────────────────────────────────────────────────────

@router.post("/trigger-rpa")
async def trigger_rpa(
    payload: dict = Body(...),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    El frontend llama a este endpoint cuando:
        a) El OCR devolvió status=READY (todos los campos completos), O
        b) El empleado corrigió los datos manualmente y hizo submit del form editable.

    El backend lanza el bot RPA en background, guarda en DB y crea la bitácora.

    Body esperado:
    {
        "invoice_data": {
            "invoice_number": "001-2024",
            "date": "2024-01-15",
            "provider": "XYZ S.A.",
            "nit": "1234567-8",
            "subtotal": 1339.29,
            "taxes": 160.71,
            "total": 1500.00
        },
        "file_path": "/app/uploads/abc123.pdf"
    }
    """
    invoice_data = payload.get("invoice_data", {})
    file_path = payload.get("file_path", "")

    if not invoice_data or not file_path:
        raise HTTPException(400, "invoice_data y file_path son requeridos.")

    rpa_service = RPAService()
    result = await rpa_service.execute_rpa_and_save(
        invoice_data=invoice_data,
        file_path=file_path,
        user_id=current_user.id,
        db=db,
    )

    return result


# ─────────────────────────────────────────────────────────────────
# POST /invoices/rpa-submit — El bot Selenium hace POST aquí
# ─────────────────────────────────────────────────────────────────

@router.post("/rpa-submit")
async def rpa_form_submit(
    payload: RPASubmitPayload,
    db: AsyncSession = Depends(get_db),
):
    """
    Recibe el submit del formulario React llenado por el bot Selenium.

    NO requiere JWT (el formulario es llenado por el bot, no por un usuario).
    En cambio, valida el RPA_SECRET_TOKEN para asegurarse de que el submit
    vino del bot y no de un cliente externo.

    Este endpoint:
        1. Valida el token
        2. Guarda la factura en la DB
        3. Crea la bitácora
        4. Retorna el invoice_id al bot (que lo incluye en el mensaje de resultado)

    El bot Selenium lee el mensaje del DOM y extrae el invoice_id de ahí.
    """
    from app.repositories.invoice_repository import InvoiceRepository
    from app.repositories.provider_repository import ProviderRepository
    from app.repositories.log_repository import LogRepository

    # ── Validar token RPA ───────────────────────────────────────
    if payload.rpa_token != RPA_SECRET_TOKEN:
        logger.warning(f"rpa-submit: Token inválido recibido.")
        raise HTTPException(403, "Token RPA inválido.")

    logger.info(f"rpa-submit: Recibido para factura '{payload.invoice_number}'")

    try:
        provider_repo = ProviderRepository(db)
        invoice_repo = InvoiceRepository(db)
        log_repo = LogRepository(db)

        # Buscar o crear proveedor
        provider = await provider_repo.get_or_create_by_nit(
            nit=payload.nit or "CF",
            name=payload.provider or "Desconocido",
        )

        # Guardar factura con status PROCESSED
        invoice_id = await invoice_repo.create(
            user_id=int(payload.user_id or 0),
            provider_id=provider.id,
            invoice_number=payload.invoice_number,
            date=payload.date,
            nit=payload.nit,
            subtotal=float(payload.subtotal or 0),
            taxes=float(payload.taxes or 0),
            total=float(payload.total or 0),
            file_path=payload.file_path or "",
            status="PROCESSED",
        )

        # Bitácora
        await log_repo.create(
            invoice_id=invoice_id,
            user_id=int(payload.user_id or 0),
            status="PROCESSED",
            rpa_result="SUCCESS",
            message="Factura registrada mediante automatización RPA.",
        )

        logger.info(f"rpa-submit: Factura guardada con ID={invoice_id}")
        return {
            "status":     "ok",
            "invoice_id": invoice_id,
            "message":    f"Factura procesada correctamente. ID: {invoice_id}",
        }

    except Exception as e:
        logger.error(f"rpa-submit: Error guardando factura: {e}", exc_info=True)
        raise HTTPException(500, f"Error al guardar la factura: {str(e)}")