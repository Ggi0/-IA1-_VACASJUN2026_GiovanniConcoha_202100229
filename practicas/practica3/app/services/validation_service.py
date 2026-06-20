"""
validation_service.py
=====================
Valida los datos extraídos por el OCR antes de pasarlos al RPA.

Reglas que aplica:
    - Todos los campos obligatorios presentes
    - NIT con formato guatemalteco válido (7-8 dígitos + guion + dígito/K, o CF)
    - Subtotal, taxes y total son números positivos
    - Total = subtotal + taxes (tolerancia del 2%)
    - Fecha parseable y no en el futuro lejano
    - Número de factura no vacío

NO escribe en la base de datos.
NO conoce el RPA ni el OCR.
Solo recibe un dict y devuelve ValidationResult.

Consumido por: invoice_service.py
"""

import re
import logging
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional

logger = logging.getLogger(__name__)

# ── Regex NIT guatemalteco ──────────────────────────────────────
# Formatos válidos: 1234567-8  |  12345678-K  |  CF  |  C/F
NIT_REGEX = re.compile(r"^\d{6,8}-[0-9K]$", re.IGNORECASE)
NIT_CF_REGEX = re.compile(r"^C\.?F\.?$", re.IGNORECASE)

# Tolerancia para verificar que total ≈ subtotal + taxes
TOTAL_TOLERANCE_PCT = 0.02  # 2%


@dataclass
class FieldError:
    field: str
    message: str


@dataclass
class ValidationResult:
    """
    Resultado de la validación.

    Attributes:
        is_valid:   True si todos los campos pasaron validación.
        errors:     Lista de errores por campo (vacía si is_valid=True).
        warnings:   Advertencias no bloqueantes (ej: total no cuadra exactamente).
        clean_data: Datos normalizados listos para el RPA (solo si is_valid=True).
    """
    is_valid: bool
    errors:   list[FieldError] = field(default_factory=list)
    warnings: list[str]        = field(default_factory=list)
    clean_data: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "errors":   [{"field": e.field, "message": e.message} for e in self.errors],
            "warnings": self.warnings,
            "clean_data": self.clean_data,
        }


class ValidationService:

    def validate(self, data: dict, db=None) -> ValidationResult:
        """
        Valida los datos extraídos por el OCR.

        Args:
            data: dict con claves:
                    invoice_number, date, provider, nit,
                    subtotal, taxes, total
            db:   Sesión de DB (opcional, para verificar duplicados).

        Returns:
            ValidationResult con is_valid y lista de errores.
        """
        errors: list[FieldError] = []
        warnings: list[str] = []

        # ── 1. Campos obligatorios presentes ──────────────────────
        required_fields = {
            "invoice_number": "Número de factura",
            "date":           "Fecha",
            "provider":       "Proveedor",
            "nit":            "NIT",
            "subtotal":       "Subtotal",
            "taxes":          "Impuestos",
            "total":          "Total",
        }

        for field_key, label in required_fields.items():
            val = data.get(field_key)
            if val is None or str(val).strip() == "" or str(val).strip() == "None":
                errors.append(FieldError(field=field_key, message=f"{label} es obligatorio."))

        # Si faltan campos obligatorios, no tiene sentido seguir validando
        if errors:
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # ── 2. Validar número de factura ──────────────────────────
        invoice_number = str(data["invoice_number"]).strip()
        if len(invoice_number) < 1 or len(invoice_number) > 50:
            errors.append(FieldError(
                field="invoice_number",
                message="Número de factura debe tener entre 1 y 50 caracteres."
            ))

        # ── 3. Validar fecha ──────────────────────────────────────
        date_str = str(data["date"]).strip()
        parsed_date = self._parse_date(date_str)
        if parsed_date is None:
            errors.append(FieldError(
                field="date",
                message=f"Fecha '{date_str}' no tiene un formato válido. Use YYYY-MM-DD."
            ))
        else:
            # Fecha no puede ser más de 10 años en el pasado ni en el futuro
            today = date.today()
            if parsed_date.year < (today.year - 10):
                warnings.append(f"La fecha {date_str} es muy antigua (más de 10 años).")
            if parsed_date > today:
                warnings.append(f"La fecha {date_str} está en el futuro.")

        # ── 4. Validar proveedor ──────────────────────────────────
        provider = str(data["provider"]).strip()
        if len(provider) < 2:
            errors.append(FieldError(
                field="provider",
                message="Nombre del proveedor debe tener al menos 2 caracteres."
            ))

        # ── 5. Validar NIT ────────────────────────────────────────
        nit = str(data["nit"]).strip().upper().replace(" ", "")
        nit_valid = NIT_REGEX.match(nit) or NIT_CF_REGEX.match(nit)
        if not nit_valid:
            errors.append(FieldError(
                field="nit",
                message=f"NIT '{nit}' no tiene formato válido. "
                        "Formatos aceptados: 1234567-8, 12345678-K, CF."
            ))

        # ── 6. Validar campos numéricos ───────────────────────────
        subtotal = self._parse_positive_number(data.get("subtotal"), "subtotal", errors)
        taxes    = self._parse_positive_number(data.get("taxes"),    "taxes",    errors)
        total    = self._parse_positive_number(data.get("total"),    "total",    errors)

        # ── 7. Validar coherencia subtotal + taxes ≈ total ────────
        if subtotal is not None and taxes is not None and total is not None:
            calculated = round(subtotal + taxes, 2)
            diff = abs(calculated - total)
            tolerance = total * TOTAL_TOLERANCE_PCT

            if diff > tolerance and diff > 0.10:
                warnings.append(
                    f"Total ({total}) no coincide exactamente con subtotal + taxes "
                    f"({subtotal} + {taxes} = {calculated}). Diferencia: {diff:.2f}."
                )

        # ── 8. Verificar duplicado (si se pasó DB) ────────────────
        is_duplicate = False
        if db is not None:
            from app.repositories.invoice_repository import InvoiceRepository
            repo = InvoiceRepository()
            existing = repo.find_duplicate(db, invoice_number, nit)
            if existing:
                is_duplicate = True
                warnings.append(
                    f"Ya existe una factura con número '{invoice_number}' y NIT '{nit}' "
                    f"(ID={existing.id}). Se marcará como duplicado."
                )

        # ── Resultado final ───────────────────────────────────────
        if errors:
            logger.warning(f"Validación FALLIDA: {[e.field for e in errors]}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Datos limpios y normalizados para el RPA
        clean_data = {
            "invoice_number": invoice_number,
            "date":           date_str,
            "provider":       provider,
            "nit":            nit,
            "subtotal":       subtotal,
            "taxes":          taxes,
            "total":          total,
            "is_duplicate":   is_duplicate,
        }

        logger.info(f"Validación EXITOSA para factura '{invoice_number}'")
        return ValidationResult(is_valid=True, warnings=warnings, clean_data=clean_data)

    # ─────────────────────────────────────────────────────────────
    # Helpers privados
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_date(date_str: str) -> Optional[date]:
        """Intenta parsear la fecha en formato ISO YYYY-MM-DD."""
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_positive_number(value, field_name: str, errors: list) -> Optional[float]:
        """
        Convierte valor a float positivo.
        Agrega error a la lista si falla.
        """
        if value is None:
            return None
        try:
            num = float(str(value).replace(",", "."))
            if num < 0:
                errors.append(FieldError(
                    field=field_name,
                    message=f"{field_name} no puede ser negativo (valor: {num})."
                ))
                return None
            return round(num, 2)
        except (ValueError, TypeError):
            errors.append(FieldError(
                field=field_name,
                message=f"{field_name} debe ser un número válido (recibido: '{value}')."
            ))
            return None