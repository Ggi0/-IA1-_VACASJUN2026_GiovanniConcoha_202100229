"""
dashboard_controller.py
=======================
Endpoints de métricas para el panel de administración.

Endpoints:
    GET /dashboard/metrics  → Totales y porcentajes del sistema
    GET /dashboard/recent   → Últimas N facturas
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
dashboard_service = DashboardService()


# ─────────────────────────────────────────────────────────────────
# GET /dashboard/metrics — Métricas generales
# ─────────────────────────────────────────────────────────────────
@router.get("/metrics")
def get_metrics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Respuesta 200:
        {
            "total_invoices": 150,
            "processed": 135,
            "pending": 5,
            "with_errors": 7,
            "rejected": 3,
            "duplicates": 4,
            "total_amount": 225000.50,
            "rpa_success_rate": 94.7
        }
    """
    return dashboard_service.get_metrics(db)


# ─────────────────────────────────────────────────────────────────
# GET /dashboard/recent — Últimas N facturas procesadas
# ─────────────────────────────────────────────────────────────────
@router.get("/recent")
def get_recent(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Query param: limit (int, default=10, máx=50)

    Respuesta 200:
        [
            {
                "id": 150,
                "invoice_number": "001-2024",
                "status": "PROCESSED",
                "total": 1500.00,
                "is_duplicate": false,
                "created_at": "2024-01-15 10:30:00"
            }
        ]
    """
    return dashboard_service.get_recent_invoices(db, limit)