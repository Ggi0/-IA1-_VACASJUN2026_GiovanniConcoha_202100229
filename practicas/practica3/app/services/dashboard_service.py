"""
dashboard_service.py
====================
Métricas y estadísticas para el panel de administración.
No escribe datos, solo los agrega y calcula.

Consume: InvoiceRepository, LogRepository
Es consumido por: dashboard_controller.py
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.invoice_model import Invoice, InvoiceStatus
from app.models.log_model import ProcessLog

logger = logging.getLogger(__name__)


class DashboardService:

    def get_metrics(self, db: Session) -> dict:
        """
        Métricas principales para el dashboard.

        Returns:
            dict con:
                total_invoices      → int
                processed           → int
                pending             → int
                with_errors         → int
                rejected            → int
                duplicates          → int
                total_amount        → float (suma de totales de facturas PROCESSED)
                rpa_success_rate    → float (% de RPA exitosos)
        """
        total       = db.query(func.count(Invoice.id)).scalar() or 0
        processed   = db.query(func.count(Invoice.id)).filter(Invoice.status == InvoiceStatus.PROCESSED).scalar() or 0
        pending     = db.query(func.count(Invoice.id)).filter(Invoice.status == InvoiceStatus.PENDING).scalar() or 0
        errors      = db.query(func.count(Invoice.id)).filter(Invoice.status == InvoiceStatus.ERROR).scalar() or 0
        rejected    = db.query(func.count(Invoice.id)).filter(Invoice.status == InvoiceStatus.REJECTED).scalar() or 0
        duplicates  = db.query(func.count(Invoice.id)).filter(Invoice.is_duplicate == True).scalar() or 0

        total_amount_row = db.query(func.sum(Invoice.total)).filter(
            Invoice.status == InvoiceStatus.PROCESSED
        ).scalar()
        total_amount = float(total_amount_row or 0)

        # RPA success rate: logs con rpa_result = SUCCESS / total logs con rpa ejecutado
        from app.models.log_model import RPAStatus
        total_rpa   = db.query(func.count(ProcessLog.id)).filter(
            ProcessLog.rpa_result != None
        ).scalar() or 0

        rpa_success = db.query(func.count(ProcessLog.id)).filter(
            ProcessLog.rpa_result == RPAStatus.SUCCESS
        ).scalar() or 0

        rpa_rate = round((rpa_success / total_rpa * 100), 1) if total_rpa > 0 else 0.0

        return {
            "total_invoices":   total,
            "processed":        processed,
            "pending":          pending,
            "with_errors":      errors,
            "rejected":         rejected,
            "duplicates":       duplicates,
            "total_amount":     round(total_amount, 2),
            "rpa_success_rate": rpa_rate,
        }

    def get_recent_invoices(self, db: Session, limit: int = 10) -> list:
        """Retorna las últimas N facturas procesadas."""
        invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).limit(limit).all()
        return [
            {
                "id":             inv.id,
                "invoice_number": inv.invoice_number,
                "status":         inv.status.value if inv.status else None,
                "total":          float(inv.total) if inv.total else None,
                "is_duplicate":   inv.is_duplicate,
                "created_at":     str(inv.created_at) if inv.created_at else None,
            }
            for inv in invoices
        ]