"""
image_utils.py
==============
Utilidades para conversión de formatos de entrada (PDF, JPG, PNG)
a imágenes np.ndarray que el preprocesador y el OCR pueden consumir.
"""

import io
import logging
from pathlib import Path
from typing import List

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# pdf2image importado de forma lazy para evitar crash si no está instalado
def _get_pdf2image():
    try:
        from pdf2image import convert_from_bytes
        return convert_from_bytes
    except ImportError:
        raise ImportError(
            "pdf2image no está instalado. "
            "Ejecuta: pip install pdf2image  y  apt-get install -y poppler-utils"
        )


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}
ALL_SUPPORTED = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_PDF_EXTENSIONS


def validate_extension(file_path: str) -> None:
    """
    Valida que el archivo tenga una extensión soportada.

    Raises:
        ValueError si la extensión no está soportada.
    """
    ext = Path(file_path).suffix.lower()
    if ext not in ALL_SUPPORTED:
        raise ValueError(
            f"Extensión '{ext}' no soportada. "
            f"Formatos válidos: {sorted(ALL_SUPPORTED)}"
        )


def load_file_as_images(file_path: str) -> List[np.ndarray]:
    """
    Carga un archivo (imagen o PDF) y lo convierte a una lista de np.ndarray BGR.

    Para imágenes: devuelve lista con 1 elemento.
    Para PDFs: devuelve una imagen por página.

    Args:
        file_path: Ruta absoluta al archivo.

    Returns:
        List[np.ndarray]: Lista de imágenes en formato BGR.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si la extensión no es soportada.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    validate_extension(file_path)

    ext = path.suffix.lower()

    if ext in SUPPORTED_PDF_EXTENSIONS:
        return _pdf_to_images(file_path)
    else:
        return _image_file_to_array(file_path)


def load_bytes_as_images(file_bytes: bytes, filename: str) -> List[np.ndarray]:
    """
    Carga un archivo desde bytes en memoria (útil cuando FastAPI recibe el upload).

    Args:
        file_bytes: Contenido del archivo en bytes.
        filename:   Nombre original del archivo (para detectar extensión).

    Returns:
        List[np.ndarray]: Lista de imágenes en formato BGR.
    """
    ext = Path(filename).suffix.lower()

    if ext not in ALL_SUPPORTED:
        raise ValueError(
            f"Extensión '{ext}' no soportada. Válidas: {sorted(ALL_SUPPORTED)}"
        )

    if ext in SUPPORTED_PDF_EXTENSIONS:
        return _pdf_bytes_to_images(file_bytes)
    else:
        return _bytes_to_image_array(file_bytes)


# ─────────────────────────────────────────────
# Helpers privados
# ─────────────────────────────────────────────

def _image_file_to_array(file_path: str) -> List[np.ndarray]:
    """Lee una imagen desde disco con OpenCV."""
    img = cv2.imread(file_path)
    if img is None:
        raise ValueError(f"OpenCV no pudo leer la imagen: {file_path}")
    logger.debug(f"Imagen cargada: {Path(file_path).name} | shape={img.shape}")
    return [img]


def _bytes_to_image_array(file_bytes: bytes) -> List[np.ndarray]:
    """Decodifica bytes de imagen a np.ndarray BGR."""
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("No se pudo decodificar la imagen desde bytes.")
    return [img]


def _pdf_to_images(file_path: str) -> List[np.ndarray]:
    """Convierte un PDF desde disco a lista de imágenes."""
    with open(file_path, "rb") as f:
        return _pdf_bytes_to_images(f.read())


def _pdf_bytes_to_images(pdf_bytes: bytes) -> List[np.ndarray]:
    """
    Convierte bytes de un PDF a lista de imágenes usando pdf2image + poppler.
    DPI=200 es suficiente para OCR de facturas; sube a 300 si el texto es pequeño.
    """
    convert_from_bytes = _get_pdf2image()

    pil_images = convert_from_bytes(pdf_bytes, dpi=200)
    logger.debug(f"PDF convertido: {len(pil_images)} página(s)")

    result = []
    for pil_img in pil_images:
        # PIL → numpy BGR
        np_img = np.array(pil_img.convert("RGB"))
        bgr = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
        result.append(bgr)

    return result


def pil_to_cv2(pil_image) -> np.ndarray:
    """Convierte imagen PIL/Pillow a np.ndarray BGR para OpenCV."""
    np_img = np.array(pil_image.convert("RGB"))
    return cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)


def cv2_to_pil(img: np.ndarray):
    """Convierte np.ndarray BGR a imagen PIL."""
    from PIL import Image
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)