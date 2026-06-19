"""
ocr_pipeline.py
===============
Pipeline OCR completo: desde bytes del archivo hasta dict con campos extraídos.

Este módulo es el ÚNICO punto de entrada que los services deben llamar.
Orquesta:
    1. image_utils   → convierte PDF/imagen a np.ndarray(s)
    2. preprocess    → limpia y mejora cada imagen con OpenCV
    3. ocr_engine    → extrae texto con Tesseract/EasyOCR
    4. invoice_parser → parsea texto a campos estructurados

Salida estándar (OCRResult) que el invoice_service consume directamente.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from app.modules.computer_vision.image_utils import load_bytes_as_images, load_file_as_images
from app.modules.computer_vision.preprocess import full_preprocess
from app.modules.ocr.ocr_engine import OCREngine
from app.modules.parser.invoice_parser import InvoiceParser

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# DATACLASS DE RESULTADO
# ─────────────────────────────────────────────────────────────────

@dataclass
class OCRResult:
    """
    Resultado estandarizado del pipeline OCR.
    Los campos son exactamente los que la tabla `invoices` necesita.
    """
    # Campos extraídos de la factura
    invoice_number: Optional[str] = None
    date:           Optional[str] = None   # YYYY-MM-DD
    provider:       Optional[str] = None
    nit:            Optional[str] = None
    subtotal:       Optional[float] = None
    taxes:          Optional[float] = None
    total:          Optional[float] = None

    # Meta-información del proceso
    raw_text:       str = ""
    pages_processed: int = 0
    processing_time_ms: float = 0.0
    engine_used:    str = ""
    confidence:     dict = field(default_factory=dict)  # campo → bool

    # Estado del pipeline
    success:        bool = False
    error_message:  Optional[str] = None

    def to_dict(self) -> dict:
        """Serializa a dict (útil para JSON responses y logs)."""
        return {
            "invoice_number":    self.invoice_number,
            "date":              self.date,
            "provider":          self.provider,
            "nit":               self.nit,
            "subtotal":          self.subtotal,
            "taxes":             self.taxes,
            "total":             self.total,
            "raw_text":          self.raw_text,
            "pages_processed":   self.pages_processed,
            "processing_time_ms": self.processing_time_ms,
            "engine_used":       self.engine_used,
            "confidence":        self.confidence,
            "success":           self.success,
            "error_message":     self.error_message,
        }

    def missing_fields(self) -> list[str]:
        """Devuelve lista de campos obligatorios que no se extrajeron."""
        required = ["invoice_number", "date", "provider", "nit", "subtotal", "taxes", "total"]
        return [f for f in required if getattr(self, f) is None]

    def is_complete(self) -> bool:
        """True si todos los campos obligatorios fueron extraídos."""
        return len(self.missing_fields()) == 0


# ─────────────────────────────────────────────────────────────────
# PIPELINE PRINCIPAL
# ─────────────────────────────────────────────────────────────────

class OCRPipeline:
    """
    Pipeline OCR reutilizable y configurable.

    Uso desde invoice_service:
        pipeline = OCRPipeline()
        result = await pipeline.process_bytes(file_bytes, "factura.pdf")

    Uso para pruebas locales:
        pipeline = OCRPipeline(engine="tesseract")
        result = await pipeline.process_file("/tmp/factura.jpg")
    """

    def __init__(
        self,
        engine: str = "auto",
        deskew: bool = True,
        merge_pages: bool = True,
    ):
        """
        Args:
            engine:      "auto" | "tesseract" | "easyocr"
            deskew:      Si True, corrige inclinación en el preprocesamiento.
            merge_pages: Si True y el PDF tiene varias páginas, concatena
                         el texto de todas las páginas antes de parsear.
        """
        self.ocr_engine = OCREngine(engine=engine)
        self.deskew = deskew
        self.merge_pages = merge_pages
        self.parser = InvoiceParser()

        logger.info(f"OCRPipeline inicializado | engine={engine} | deskew={deskew}")

    # ─────────────────────────────────────────────
    # API pública
    # ─────────────────────────────────────────────

    async def process_bytes(self, file_bytes: bytes, filename: str) -> OCRResult:
        """
        Procesa un archivo recibido como bytes (upload de FastAPI).

        Args:
            file_bytes: Contenido del archivo en bytes.
            filename:   Nombre original del archivo (para detectar extensión).

        Returns:
            OCRResult con los campos extraídos.
        """
        start = time.monotonic()
        result = OCRResult()

        try:
            images = load_bytes_as_images(file_bytes, filename)
            result = self._process_images(images)
        except Exception as e:
            logger.error(f"Error en pipeline OCR: {e}", exc_info=True)
            result.success = False
            result.error_message = str(e)

        result.processing_time_ms = round((time.monotonic() - start) * 1000, 2)
        result.engine_used = self.ocr_engine.engine_type.value
        return result

    async def process_file(self, file_path: str) -> OCRResult:
        """
        Procesa un archivo directamente desde disco.
        Útil para scripts de prueba y workers asíncronos.

        Args:
            file_path: Ruta absoluta al archivo.

        Returns:
            OCRResult con los campos extraídos.
        """
        start = time.monotonic()
        result = OCRResult()

        try:
            images = load_file_as_images(file_path)
            result = self._process_images(images)
        except Exception as e:
            logger.error(f"Error en pipeline OCR (file): {e}", exc_info=True)
            result.success = False
            result.error_message = str(e)

        result.processing_time_ms = round((time.monotonic() - start) * 1000, 2)
        result.engine_used = self.ocr_engine.engine_type.value
        return result

    # ─────────────────────────────────────────────
    # Proceso interno
    # ─────────────────────────────────────────────

    def _process_images(self, images: list[np.ndarray]) -> OCRResult:
        """
        Recibe la lista de imágenes (una por página en PDF),
        las preprocesa, extrae texto y parsea.
        """
        result = OCRResult()
        result.pages_processed = len(images)

        texts = []
        for i, img in enumerate(images):
            logger.debug(f"Procesando página {i + 1}/{len(images)}")
            processed = full_preprocess(img, deskew_enabled=self.deskew)
            text = self.ocr_engine.extract_text(processed)
            logger.debug(f"Página {i + 1} — {len(text)} caracteres extraídos")
            texts.append(text)

        if self.merge_pages:
            combined_text = "\n\n--- PÁGINA ---\n\n".join(texts)
        else:
            # Usar solo la primera página (suficiente para la mayoría de facturas)
            combined_text = texts[0] if texts else ""

        result.raw_text = combined_text

        # Parsear campos
        parsed = self.parser.parse(combined_text)

        result.invoice_number = parsed.get("invoice_number")
        result.date           = parsed.get("date")
        result.provider       = parsed.get("provider")
        result.nit            = parsed.get("nit")
        result.subtotal       = parsed.get("subtotal")
        result.taxes          = parsed.get("taxes")
        result.total          = parsed.get("total")
        result.confidence     = parsed.get("_confidence", {})

        result.success = True
        return result


# ─────────────────────────────────────────────────────────────────
# Singleton global (reutiliza el modelo EasyOCR ya cargado)
# ─────────────────────────────────────────────────────────────────

_pipeline_instance: Optional[OCRPipeline] = None


def get_ocr_pipeline(engine: str = "auto") -> OCRPipeline:
    """
    Devuelve el singleton del pipeline.
    Importante para EasyOCR: el modelo se carga una sola vez en RAM.

    Uso en FastAPI (dependency injection):
        pipeline = get_ocr_pipeline()

    Uso en invoice_service:
        from app.modules.ocr.ocr_pipeline import get_ocr_pipeline
        pipeline = get_ocr_pipeline()
        result = await pipeline.process_bytes(file_bytes, filename)
    """
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = OCRPipeline(engine=engine)
    return _pipeline_instance