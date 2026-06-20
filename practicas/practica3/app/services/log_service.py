"""
log_service.py
==============
Servicio para consultar la bitácora de procesamiento.
La escritura de logs la hacen invoice_service e rpa_service directamente
vía log_repository. Este service expone las CONSULTAS.

Consume: LogRepository
Es consumido por: dashboard_controller.py, invoice_controller.py
"""

import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.log_repository import LogRepository
from app.repositories.invoice_repository import InvoiceRepository

logger = logging.getLogger(__name__)


class LogService:

    def __init__(self):
        self.log_repo     = LogRepository()
        self.invoice_repo = InvoiceRepository()

    def get_all_logs(self, db: Session) -> list:
        """Retorna todos los registros de la bitácora, ordenados por fecha desc."""
        logs = self.log_repo.get_all_logs(db)
        return [self._serialize(log) for log in logs]

    def get_logs_by_invoice(self, db: Session, invoice_id: int) -> list:
        """Retorna los logs de una factura específica."""
        invoice = self.invoice_repo.get_by_id(db, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail=f"Factura ID {invoice_id} no encontrada.")
        logs = self.log_repo.get_logs_by_invoice(db, invoice_id)
        return [self._serialize(log) for log in logs]

    @staticmethod
    def _serialize(log) -> dict:
        return {
            "id":           log.id,
            "invoice_id":   log.invoice_id,
            "user_id":      log.user_id,
            "process_date": str(log.process_date) if log.process_date else None,
            "status":       log.status.value     if log.status     else None,
            "rpa_result":   log.rpa_result.value if log.rpa_result else None,
            "message":      log.message,
        }