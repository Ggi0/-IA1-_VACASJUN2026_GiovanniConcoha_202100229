"""
ocr_engine.py
=============
Motor OCR con soporte para Tesseract y EasyOCR.
Expone una interfaz unificada: extract_text(img) → str.

Selección de motor:
  - Por defecto se usa Tesseract (más liviano, bueno para texto impreso limpio).
  - EasyOCR se usa como fallback o cuando Tesseract devuelve texto vacío/pobre.
  - Se puede forzar un motor con OCREngine(engine="easyocr").
"""

import logging
from enum import Enum
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class EngineType(str, Enum):
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    AUTO = "auto"       # Tesseract primero, EasyOCR como fallback


class OCREngine:
    """
    Motor OCR unificado.

    Uso:
        engine = OCREngine(engine="auto")
        text = engine.extract_text(preprocessed_image)
    """

    def __init__(self, engine: str = "auto", languages: list[str] = None):
        """
        Args:
            engine:    "tesseract" | "easyocr" | "auto"
            languages: Lista de idiomas. Ej: ["es", "en"]
                       Para Tesseract usa códigos ISO 3166 (spa, eng).
                       Para EasyOCR usa códigos de 2 letras (es, en).
        """
        self.engine_type = EngineType(engine)
        self.languages = languages or ["es", "en"]

        self._tesseract_available = False
        self._easyocr_reader = None

        self._init_engines()

    # ─────────────────────────────────────────────
    # Inicialización
    # ─────────────────────────────────────────────

    def _init_engines(self):
        """Detecta y prepara los motores disponibles."""
        if self.engine_type in (EngineType.TESSERACT, EngineType.AUTO):
            self._check_tesseract()

        if self.engine_type == EngineType.EASYOCR:
            self._init_easyocr()

    def _check_tesseract(self):
        """Verifica que pytesseract y el binario de Tesseract estén disponibles."""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            self._tesseract_available = True
            logger.info("Tesseract OCR disponible.")
        except Exception as e:
            logger.warning(f"Tesseract no disponible: {e}")
            self._tesseract_available = False

    def _init_easyocr(self):
        """Carga el reader de EasyOCR (carga el modelo en RAM, puede tardar)."""
        try:
            import easyocr
            # gpu=False para compatibilidad en contenedores sin GPU
            self._easyocr_reader = easyocr.Reader(
                self.languages,
                gpu=False,
                verbose=False
            )
            logger.info(f"EasyOCR inicializado con idiomas: {self.languages}")
        except Exception as e:
            logger.error(f"No se pudo inicializar EasyOCR: {e}")
            raise

    def _get_easyocr_reader(self):
        """Carga EasyOCR de forma lazy (solo cuando se necesita)."""
        if self._easyocr_reader is None:
            self._init_easyocr()
        return self._easyocr_reader

    # ─────────────────────────────────────────────
    # API pública
    # ─────────────────────────────────────────────

    def extract_text(self, img: np.ndarray) -> str:
        """
        Extrae texto de una imagen preprocesada.

        Args:
            img: np.ndarray — imagen en escala de grises, ya preprocesada.

        Returns:
            str: Texto extraído, limpio de caracteres de control innecesarios.
        """
        if self.engine_type == EngineType.TESSERACT:
            return self._run_tesseract(img)

        elif self.engine_type == EngineType.EASYOCR:
            return self._run_easyocr(img)

        else:  # AUTO
            return self._run_auto(img)

    def extract_text_with_confidence(self, img: np.ndarray) -> dict:
        """
        Extrae texto junto con el nivel de confianza promedio del OCR.

        Returns:
            dict con keys:
                'text'       → str  : texto extraído
                'confidence' → float: confianza promedio (0–100)
                'engine'     → str  : motor que se usó
        """
        if self.engine_type in (EngineType.TESSERACT, EngineType.AUTO) and self._tesseract_available:
            return self._tesseract_with_confidence(img)
        else:
            text = self._run_easyocr(img)
            return {"text": text, "confidence": -1.0, "engine": "easyocr"}

    # ─────────────────────────────────────────────
    # Implementaciones internas
    # ─────────────────────────────────────────────

    def _run_tesseract(self, img: np.ndarray) -> str:
        """Ejecuta Tesseract OCR sobre la imagen."""
        import pytesseract
        from PIL import Image

        # Tesseract espera PIL Image o path; convertimos desde numpy
        pil_img = Image.fromarray(img)

        # lang: "spa+eng" para facturas guatemaltecas
        tess_lang = "spa+eng"

        # PSM 6: Assumes a single uniform block of text (facturas)
        config = "--psm 6 --oem 3"

        text = pytesseract.image_to_string(pil_img, lang=tess_lang, config=config)
        return self._clean_text(text)

    def _run_easyocr(self, img: np.ndarray) -> str:
        """Ejecuta EasyOCR sobre la imagen."""
        reader = self._get_easyocr_reader()
        results = reader.readtext(img, detail=0, paragraph=True)
        text = "\n".join(results)
        return self._clean_text(text)

    def _run_auto(self, img: np.ndarray) -> str:
        """
        Intenta Tesseract primero. Si el resultado tiene menos de 20 caracteres,
        usa EasyOCR como fallback.
        """
        if self._tesseract_available:
            text = self._run_tesseract(img)
            if len(text.strip()) >= 20:
                logger.debug("AUTO: Tesseract OK.")
                return text
            logger.debug(f"AUTO: Tesseract devolvió texto corto ({len(text.strip())} chars). Usando EasyOCR.")

        return self._run_easyocr(img)

    def _tesseract_with_confidence(self, img: np.ndarray) -> dict:
        """Obtiene texto y confianza promedio de Tesseract."""
        import pytesseract
        from PIL import Image
        import pandas as pd

        pil_img = Image.fromarray(img)
        data = pytesseract.image_to_data(
            pil_img, lang="spa+eng", config="--psm 6 --oem 3",
            output_type=pytesseract.Output.DATAFRAME
        )

        # Filtrar solo las palabras con confianza >= 0
        words = data[data["conf"] > 0]
        confidence = float(words["conf"].mean()) if not words.empty else 0.0
        text = " ".join(words["text"].dropna().tolist())

        return {
            "text": self._clean_text(text),
            "confidence": round(confidence, 2),
            "engine": "tesseract"
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Limpieza básica del texto extraído:
        - Elimina líneas completamente vacías múltiples.
        - Elimina caracteres de control raros (excepto \\n).
        - Elimina espacios al inicio/fin.
        """
        import re
        # Reemplaza caracteres de control raros (excepto \n \t)
        text = re.sub(r"[^\S\n\t ]+", " ", text)
        # Colapsa líneas vacías múltiples en una sola
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()