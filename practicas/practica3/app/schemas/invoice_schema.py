"""
invoice_schema.py
=================
Schemas Pydantic para validar los bodies de los endpoints de facturas.
FastAPI los usa automáticamente para validar la request antes de
llamar al controller.
"""

from typing import Optional
from pydantic import BaseModel


# ─────────────────────────────────────────────────────────────────
# POST /invoices/validate
# Datos corregidos manualmente por el empleado en el form editable.
# ─────────────────────────────────────────────────────────────────
class ValidatePayload(BaseModel):
    invoice_number: Optional[str] = None
    date:           Optional[str] = None
    provider:       Optional[str] = None
    nit:            Optional[str] = None
    subtotal:       Optional[float] = None
    taxes:          Optional[float] = None
    total:          Optional[float] = None


# ─────────────────────────────────────────────────────────────────
# POST /invoices/trigger-rpa
# Los datos validados + la ruta del archivo guardado.
# ─────────────────────────────────────────────────────────────────
class TriggerRPAPayload(BaseModel):
    invoice_data: dict   # Los campos de la factura (validados)
    file_path:    str    # Ruta en disco: "/app/uploads/abc123.pdf"


# ─────────────────────────────────────────────────────────────────
# POST /invoices/rpa-submit
# Enviado por el formulario React que el bot Selenium llenó.
# Todos los valores numéricos llegan como string porque vienen de inputs HTML.
# ─────────────────────────────────────────────────────────────────
class RPASubmitPayload(BaseModel):
    rpa_token:      str                  # Token secreto interno

    invoice_number: Optional[str] = None
    date:           Optional[str] = None
    provider:       Optional[str] = None
    nit:            Optional[str] = None
    subtotal:       Optional[str] = None  # String desde el input HTML
    taxes:          Optional[str] = None
    total:          Optional[str] = None
    file_path:      Optional[str] = None
    user_id:        Optional[str] = None  # String desde el input hidden

    class Config:
        extra = "ignore"                  # Ignorar campos extras del form