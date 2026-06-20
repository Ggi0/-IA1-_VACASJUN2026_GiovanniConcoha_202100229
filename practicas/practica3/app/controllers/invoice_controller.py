"""
invoice_controller.py
=====================
Endpoints del flujo principal de facturas.

Endpoints:
    POST /invoices/upload         → Recibe archivo, corre OCR, valida
    POST /invoices/validate       → Valida datos corregidos manualmente
    POST /invoices/trigger-rpa    → Dispara el bot Selenium
    POST /invoices/rpa-submit     → Recibe el submit del formulario React (bot)
    GET  /invoices                → Lista facturas
    GET  /invoices/{id}           → Detalle de una factura
    GET  /invoices/{id}/logs      → Bitácora de una factura

FLUJO COMPLETO (ver API_ENDPOINTS.md para detalle):
    upload → [READY] → trigger-rpa → rpa-submit (interno) → DB + bitácora
          → [NEEDS_REVIEW] → validate → trigger-rpa → ...
"""

from fastapi import APIRouter, Depends, UploadFile, File, Body, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.invoice_service import InvoiceService
from app.schemas.invoice_schema import RPASubmitPayload, TriggerRPAPayload, ValidatePayload

router = APIRouter(prefix="/invoices", tags=["Invoices"])
invoice_service = InvoiceService()


# ═══════════════════════════════════════════════════════════════════
# POST /invoices/upload
# PASOS 2, 3, 4, 5 del flujo.
# El empleado sube el archivo. Este endpoint lo recibe, corre el
# OCR y la validación automática. Devuelve READY, NEEDS_REVIEW o ERROR.
# ═══════════════════════════════════════════════════════════════════
@router.post("/upload")
async def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Content-Type: multipart/form-data
    Campo: file (PDF, JPG, JPEG, PNG — máx 10MB)

    Respuesta posible A — status=READY:
        Todo extraído y validado. El frontend llama a /trigger-rpa.

    Respuesta posible B — status=NEEDS_REVIEW:
        Faltan campos o hay errores. El frontend muestra form editable.

    Respuesta posible C — status=ERROR:
        Fallo técnico del OCR (archivo corrompido, formato no legible).
    """
    return await invoice_service.upload_and_process(
        file=file,
        user_id=current_user.id,
        db=db,
    )


# ═══════════════════════════════════════════════════════════════════
# POST /invoices/validate
# PASO 5b — corrección manual del empleado.
# El empleado editó los campos en el formulario y hace submit.
# Este endpoint valida esos datos corregidos antes de ir al RPA.
# ═══════════════════════════════════════════════════════════════════
@router.post("/validate")
def validate_invoice(
    body: ValidatePayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Body:
        {
            "invoice_number": "001-2024",
            "date": "2024-01-15",
            "provider": "XYZ S.A.",
            "nit": "1234567-8",
            "subtotal": 1339.29,
            "taxes": 160.71,
            "total": 1500.00
        }

    Respuesta si is_valid=true  → frontend llama a /trigger-rpa con clean_data
    Respuesta si is_valid=false → frontend muestra los errores en el form
    """
    return invoice_service.validate_manual(
        data=body.model_dump(),
        db=db,
    )


# ═══════════════════════════════════════════════════════════════════
# POST /invoices/trigger-rpa
# PASOS 6, 7, 8 del flujo.
# El frontend llama aquí después de que los datos están validados.
# Este endpoint lanza el bot Selenium en un thread, espera el resultado,
# y devuelve el estado final (la DB ya fue escrita por rpa-submit).
# IMPORTANTE: puede tardar 5–20 segundos. El frontend debe mostrar loading.
# ═══════════════════════════════════════════════════════════════════
@router.post("/trigger-rpa")
async def trigger_rpa(
    body: TriggerRPAPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Body:
        {
            "invoice_data": {
                "invoice_number": "001-2024",
                "date": "2024-01-15",
                "provider": "XYZ S.A.",
                "nit": "1234567-8",
                "subtotal": 1339.29,
                "taxes": 160.71,
                "total": 1500.00,
                "is_duplicate": false
            },
            "file_path": "/app/uploads/abc123.pdf"
        }

    Respuesta éxito:
        { "success": true, "invoice_id": 42, "rpa_status": "SUCCESS", "duration_ms": 8340 }

    Respuesta fallo RPA (factura guardada como ERROR):
        { "success": false, "invoice_id": 43, "rpa_status": "FAILED", "rpa_message": "..." }
    """
    return await invoice_service.trigger_rpa_flow(
        invoice_data=body.invoice_data,
        file_path=body.file_path,
        user_id=current_user.id,
        db=db,
    )


# ═══════════════════════════════════════════════════════════════════
# POST /invoices/rpa-submit
# ENDPOINT INTERNO — lo llama el formulario React /rpa-form,
# que fue abierto y llenado por el bot Selenium.
# NO lo llama el empleado directamente.
# Valida el rpa_token secreto, guarda en DB y crea la bitácora.
# ═══════════════════════════════════════════════════════════════════
@router.post("/rpa-submit")
def rpa_submit(payload: dict, db: Session = Depends(get_db)):
    return invoice_service.rpa_submit(payload, db)
    """
    Body (enviado por el formulario React):
        {
            "rpa_token": "smartinvoice-rpa-secret-2024",
            "invoice_number": "001-2024",
            "date": "2024-01-15",
            "provider": "XYZ S.A.",
            "nit": "1234567-8",
            "subtotal": "1339.29",
            "taxes": "160.71",
            "total": "1500.00",
            "file_path": "/app/uploads/abc123.pdf",
            "user_id": "1"
        }

    Respuesta 200:
        { "status": "ok", "invoice_id": 42, "message": "Factura procesada correctamente. ID: 42" }
    
    return invoice_service.rpa_submit(
        payload=body.model_dump(),
        rpa_token=body.rpa_token,
        db=db,
    )
    """


# ═══════════════════════════════════════════════════════════════════
# GET /invoices
# Lista facturas. ADMIN ve todas. EMPLOYEE ve solo las suyas.
# ═══════════════════════════════════════════════════════════════════
@router.get("/")
def get_invoices(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Respuesta 200: lista de objetos factura con todos sus campos.
    """
    invoices = invoice_service.get_all(db)

    # EMPLOYEE solo ve las suyas
    if current_user.role.value == "EMPLOYEE":
        invoices = [inv for inv in invoices if inv["user_id"] == current_user.id]

    return invoices


# ═══════════════════════════════════════════════════════════════════
# GET /invoices/{id}
# Detalle de una factura por ID.
# ═══════════════════════════════════════════════════════════════════
@router.get("/{invoice_id}")
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Path param: invoice_id (int)
    Respuesta 200: objeto factura completo.
    Error 404: factura no encontrada.
    """
    invoice = invoice_service.get_by_id(db, invoice_id)

    # EMPLOYEE no puede ver facturas de otros
    if current_user.role.value == "EMPLOYEE" and invoice["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta factura.")

    return invoice


# ═══════════════════════════════════════════════════════════════════
# GET /invoices/{id}/logs
# Bitácora de una factura específica.
# ═══════════════════════════════════════════════════════════════════
@router.get("/{invoice_id}/logs")
def get_invoice_logs(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Path param: invoice_id (int)
    Respuesta 200: lista de entradas de bitácora para esa factura.
    Error 404: factura no encontrada.
    """
    return invoice_service.get_logs(db, invoice_id)