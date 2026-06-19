"""
patterns.py
===========
Patrones regex centralizados para extracción de datos de facturas.
Facturas guatemaltecas (SAT) como referencia principal.

Todos los patrones son CASE-INSENSITIVE y soportan variaciones
tipográficas comunes del OCR (espacios extra, dos puntos opcionales, etc.).
"""

import re

# ─────────────────────────────────────────────────────────────────
# NÚMERO DE FACTURA
# ─────────────────────────────────────────────────────────────────
# Soporta: "Factura No. 001-2024", "No. Factura: A-0012", "FACTURA #1234"
INVOICE_NUMBER_PATTERNS = [
    r"(?:factura|invoice|fact\.?)\s*(?:no\.?|n[uú]mero|number|#)?\s*[:.]?\s*([A-Z0-9\-\/]+)",
    r"(?:no\.?|n[uú]mero|number)\s*(?:de\s+)?(?:factura|invoice)\s*[:.]?\s*([A-Z0-9\-\/]+)",
    r"#\s*([A-Z0-9\-\/]{3,20})",
    r"(?:serie|serie\s+y\s+n[uú]mero)\s*[:.]?\s*([A-Z0-9\-\/]+)",
]

# ─────────────────────────────────────────────────────────────────
# FECHA
# ─────────────────────────────────────────────────────────────────
# Formatos: "01/02/2024", "2024-01-02", "01 de enero de 2024"
DATE_PATTERNS = [
    # DD/MM/YYYY o MM/DD/YYYY
    r"(?:fecha\s*[:.]?\s*)?(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
    # YYYY-MM-DD (ISO)
    r"(\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})",
    # "01 de enero de 2024"
    r"(\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(?:de\s+)?\d{4})",
    # "enero 01, 2024"
    r"((?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{1,2},?\s*\d{4})",
]

# ─────────────────────────────────────────────────────────────────
# NIT (Guatemala)
# ─────────────────────────────────────────────────────────────────
# NIT guatemalteco: 6-8 dígitos + guion + dígito verificador (o K)
# Ejemplos: 1234567-8, 12345678-K, CF (consumidor final)
NIT_PATTERNS = [
    r"(?:nit|n\.i\.t\.?|registro)\s*[:.]?\s*(\d{6,8}-[0-9K])",
    r"(?:nit|n\.i\.t\.?)\s*[:.]?\s*(\d{6,8}\s*-\s*[0-9K])",
    # Consumidor Final como caso especial
    r"(?:nit|n\.i\.t\.?)\s*[:.]?\s*(C\.?F\.?)",
    # Sin guion (OCR puede omitirlo)
    r"(?:nit|n\.i\.t\.?)\s*[:.]?\s*(\d{7,9})",
]

# ─────────────────────────────────────────────────────────────────
# NOMBRE DEL PROVEEDOR / EMPRESA EMISORA
# ─────────────────────────────────────────────────────────────────
PROVIDER_PATTERNS = [
    r"(?:proveedor|empresa|emisor|vendedor|raz[oó]n\s+social)\s*[:.]?\s*(.+?)(?:\n|$)",
    r"(?:nombre|company|supplier)\s*[:.]?\s*(.+?)(?:\n|$)",
]

# ─────────────────────────────────────────────────────────────────
# SUBTOTAL
# ─────────────────────────────────────────────────────────────────
SUBTOTAL_PATTERNS = [
    r"(?:subtotal|sub[-\s]?total|base\s+imponible)\s*[:.]?\s*(?:Q|GTQ|L|USD|\$)?\s*([\d,\.]+)",
    r"(?:subtotal|sub\s+total)\s*\n?\s*(?:Q|GTQ)?\s*([\d,\.]+)",
]

# ─────────────────────────────────────────────────────────────────
# IMPUESTOS (IVA / ISR)
# ─────────────────────────────────────────────────────────────────
TAX_PATTERNS = [
    r"(?:iva|impuesto|tax|impuestos|i\.v\.a\.?)\s*[:.]?\s*(?:\d+\s*%\s*)?(?:Q|GTQ|L|USD|\$)?\s*([\d,\.]+)",
    r"(?:iva|impuesto)\s*\n?\s*(?:Q|GTQ)?\s*([\d,\.]+)",
]

# ─────────────────────────────────────────────────────────────────
# TOTAL
# ─────────────────────────────────────────────────────────────────
TOTAL_PATTERNS = [
    r"(?:total\s+a\s+pagar|gran\s+total|total\s+factura|monto\s+total|total\s+general)\s*[:.]?\s*(?:Q|GTQ|L|USD|\$)?\s*([\d,\.]+)",
    r"\btotal\b\s*[:.]?\s*(?:Q|GTQ|L|USD|\$)?\s*([\d,\.]+)",
]


# ─────────────────────────────────────────────────────────────────
# Compilar todos los patrones con re.IGNORECASE
# ─────────────────────────────────────────────────────────────────

def _compile_list(patterns: list[str]) -> list[re.Pattern]:
    return [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in patterns]


COMPILED = {
    "invoice_number": _compile_list(INVOICE_NUMBER_PATTERNS),
    "date":           _compile_list(DATE_PATTERNS),
    "nit":            _compile_list(NIT_PATTERNS),
    "provider":       _compile_list(PROVIDER_PATTERNS),
    "subtotal":       _compile_list(SUBTOTAL_PATTERNS),
    "taxes":          _compile_list(TAX_PATTERNS),
    "total":          _compile_list(TOTAL_PATTERNS),
}