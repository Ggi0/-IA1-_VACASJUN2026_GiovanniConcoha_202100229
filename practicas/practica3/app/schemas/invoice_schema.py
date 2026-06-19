"""
invoice_schema.py — schemas relacionados con el flujo RPA
==========================================================
Agrega RPASubmitPayload a tu invoice_schema.py existente.
"""

from typing import Optional
from pydantic import BaseModel


class RPASubmitPayload(BaseModel):
    """
    Payload que el formulario React envía al endpoint POST /invoices/rpa-submit.
    El bot Selenium llena estos campos y hace submit.

    Todos los campos son Optional porque:
    - El bot puede fallar llenando alguno
    - El backend valida primero el token, luego los datos
    """
    # Token de seguridad interna (no JWT)
    rpa_token: str

    # Campos de la factura
    invoice_number: Optional[str] = None
    date:           Optional[str] = None
    provider:       Optional[str] = None
    nit:            Optional[str] = None
    subtotal:       Optional[str] = None   # Llega como string desde el form
    taxes:          Optional[str] = None
    total:          Optional[str] = None

    # Campos ocultos del form
    file_path: Optional[str] = None
    user_id:   Optional[str] = None        # Llega como string desde el form

    class Config:
        # Permite campos extra (por si el form envía algo adicional)
        extra = "ignore"