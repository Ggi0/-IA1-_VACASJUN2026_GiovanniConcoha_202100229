"""
invoice_parser.py
=================
Extrae campos estructurados de la factura a partir del texto OCR crudo.

Retorna un dict con los campos extraídos y un sub-dict de confianza
por campo (True si se encontró, False si no).

Flujo:
    raw_text (str)
        └─► InvoiceParser.parse(text)
                └─► dict con: invoice_number, date, provider, nit,
                              subtotal, taxes, total, _confidence
"""

import re
import logging
from datetime import datetime
from typing import Optional

from app.modules.parser.patterns import COMPILED

logger = logging.getLogger(__name__)

# Meses en español para normalización de fechas
MONTHS_ES = {
    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12",
}


class InvoiceParser:
    """
    Parser de facturas basado en regex.
    Stateless: cada llamada a parse() es independiente.
    """

    def parse(self, text: str) -> dict:
        """
        Extrae los campos de la factura desde el texto OCR.

        Args:
            text: Texto plano extraído por el motor OCR.

        Returns:
            dict con las claves:
                invoice_number  : str | None
                date            : str | None  (formato ISO: YYYY-MM-DD)
                provider        : str | None
                nit             : str | None
                subtotal        : float | None
                taxes           : float | None
                total           : float | None
                raw_text        : str          (texto original, para debug)
                _confidence     : dict         (campo → bool)
        """
        result = {
            "invoice_number": self._extract_first(text, "invoice_number"),
            "date":           self._extract_date(text),
            "provider":       self._extract_provider(text),
            "nit":            self._extract_nit(text),
            "subtotal":       self._extract_number(text, "subtotal"),
            "taxes":          self._extract_number(text, "taxes"),
            "total":          self._extract_total(text),
            "raw_text":       text,
        }

        # Registrar confianza por campo
        result["_confidence"] = {
            k: v is not None
            for k, v in result.items()
            if k not in ("raw_text", "_confidence")
        }

        found = sum(result["_confidence"].values())
        total_fields = len(result["_confidence"])
        logger.info(f"Parser: {found}/{total_fields} campos extraídos.")

        return result

    # ─────────────────────────────────────────────
    # Extractores por campo
    # ─────────────────────────────────────────────

    def _extract_first(self, text: str, field: str) -> Optional[str]:
        """
        Busca el primer match válido de los patrones del campo.
        Devuelve el grupo 1 limpio, o None si no encuentra.
        """
        for pattern in COMPILED[field]:
            match = pattern.search(text)
            if match:
                value = match.group(1).strip()
                if value:
                    logger.debug(f"[{field}] match: '{value}'")
                    return value
        logger.debug(f"[{field}] no match.")
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """
        Extrae la fecha y la normaliza a formato ISO YYYY-MM-DD.
        """
        raw = self._extract_first(text, "date")
        if not raw:
            return None
        return self._normalize_date(raw)

    def _extract_nit(self, text: str) -> Optional[str]:
        """
        Extrae el NIT y lo normaliza (elimina espacios alrededor del guion).
        """
        raw = self._extract_first(text, "nit")
        if not raw:
            return None
        # Normalizar: quitar espacios alrededor del guion
        normalized = re.sub(r"\s*-\s*", "-", raw).upper().strip()
        return normalized

    def _extract_provider(self, text: str) -> Optional[str]:
        """
        Extrae el nombre del proveedor.
        Limita a 150 caracteres y elimina saltos de línea internos.
        """
        raw = self._extract_first(text, "provider")
        if not raw:
            return None
        clean = re.sub(r"\s+", " ", raw).strip()[:150]
        return clean if len(clean) > 2 else None

    def _extract_number(self, text: str, field: str) -> Optional[float]:
        """
        Extrae un campo numérico y lo convierte a float.
        Soporta: "1,500.00", "1.500,00", "1500"
        """
        raw = self._extract_first(text, field)
        return self._parse_number(raw)

    def _extract_total(self, text: str) -> Optional[float]:
        """
        Extrae el total. Si no lo encuentra con su propio patrón,
        intenta calcularlo: subtotal + taxes.
        """
        total = self._extract_number(text, "total")
        if total is not None:
            return total

        # Fallback: calcular desde subtotal + taxes
        subtotal = self._extract_number(text, "subtotal")
        taxes = self._extract_number(text, "taxes")
        if subtotal is not None and taxes is not None:
            calculated = round(subtotal + taxes, 2)
            logger.debug(f"[total] calculado: {subtotal} + {taxes} = {calculated}")
            return calculated

        return None

    # ─────────────────────────────────────────────
    # Helpers de normalización
    # ─────────────────────────────────────────────

    @staticmethod
    def _parse_number(raw: Optional[str]) -> Optional[float]:
        """
        Convierte una cadena numérica a float.
        Maneja tanto '1,500.00' (US) como '1.500,00' (EU).
        """
        if not raw:
            return None
        # Limpiar caracteres no numéricos excepto . y ,
        clean = re.sub(r"[^\d,\.]", "", raw)
        if not clean:
            return None

        # Detectar formato
        has_comma = "," in clean
        has_dot = "." in clean

        if has_comma and has_dot:
            # Determinar cuál es el separador decimal
            last_comma = clean.rfind(",")
            last_dot = clean.rfind(".")
            if last_comma > last_dot:
                # Formato EU: 1.500,00
                clean = clean.replace(".", "").replace(",", ".")
            else:
                # Formato US: 1,500.00
                clean = clean.replace(",", "")
        elif has_comma:
            # Solo comas: "1,500" o "1,5"
            parts = clean.split(",")
            if len(parts) == 2 and len(parts[1]) <= 2:
                clean = clean.replace(",", ".")
            else:
                clean = clean.replace(",", "")

        try:
            return round(float(clean), 2)
        except ValueError:
            logger.warning(f"No se pudo convertir a número: '{raw}' → '{clean}'")
            return None

    @staticmethod
    def _normalize_date(raw: str) -> Optional[str]:
        """
        Normaliza una fecha a formato ISO YYYY-MM-DD.
        Soporta múltiples formatos de entrada.
        """
        raw = raw.strip().lower()

        # "01 de enero de 2024" o "enero 01, 2024"
        for month_es, month_num in MONTHS_ES.items():
            if month_es in raw:
                raw = raw.replace("de", "").replace(",", "")
                raw = re.sub(r"\s+", " ", raw).strip()
                parts = raw.split()
                parts_no_month = [p for p in parts if p != month_es]
                if len(parts_no_month) >= 2:
                    day = parts_no_month[0].zfill(2)
                    year = parts_no_month[1] if len(parts_no_month[1]) == 4 else parts_no_month[0]
                    day = parts_no_month[0].zfill(2) if len(parts_no_month[0]) <= 2 else parts_no_month[1].zfill(2)
                    try:
                        return f"{year}-{month_num}-{day}"
                    except Exception:
                        pass

        # Formatos numéricos: DD/MM/YYYY, YYYY-MM-DD, DD.MM.YYYY
        separators = r"[\/\-\.]"
        parts = re.split(separators, raw)
        if len(parts) == 3:
            a, b, c = parts
            # YYYY-MM-DD
            if len(a) == 4:
                return f"{a}-{b.zfill(2)}-{c.zfill(2)}"
            # DD/MM/YYYY
            if len(c) == 4:
                return f"{c}-{b.zfill(2)}-{a.zfill(2)}"
            # YY/MM/DD (poco común)
            if len(a) == 2:
                year = f"20{a}" if int(a) < 50 else f"19{a}"
                return f"{year}-{b.zfill(2)}-{c.zfill(2)}"

        logger.warning(f"No se pudo normalizar fecha: '{raw}'")
        return raw  # Devolver sin normalizar si no se puede parsear