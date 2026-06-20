"""
log_controller.py
=================
Endpoints de consulta de la bitácora.

Endpoints:
    GET /logs           → Toda la bitácora (ADMIN)
    GET /logs/{invoice_id} → Logs de una factura específica
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.services.log_service import LogService

router = APIRouter(prefix="/logs", tags=["Logs"])
log_service = LogService()


# ─────────────────────────────────────────────────────────────────
# GET /logs — Toda la bitácora (solo ADMIN)
# ─────────────────────────────────────────────────────────────────
@router.get("/")
def get_all_logs(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """
    Respuesta 200: lista completa de entradas de bitácora con:
        id, invoice_id, user_id, process_date, status, rpa_result, message
    """
    return log_service.get_all_logs(db)


# ─────────────────────────────────────────────────────────────────
# GET /logs/{invoice_id} — Logs de una factura específica
# Cualquier usuario autenticado puede ver los logs de una factura.
# ─────────────────────────────────────────────────────────────────
@router.get("/{invoice_id}")
def get_logs_by_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Path param: invoice_id (int)
    Error 404: factura no encontrada.
    """
    return log_service.get_logs_by_invoice(db, invoice_id)