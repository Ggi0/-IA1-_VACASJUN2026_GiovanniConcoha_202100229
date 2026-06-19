"""
preprocess.py
=============
Módulo de preprocesamiento de imágenes con OpenCV.
Se encarga de limpiar, enderezar y mejorar la calidad de la imagen
antes de pasarla al motor OCR.
"""

import cv2
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def load_image(file_path: str) -> np.ndarray:
    """
    Carga una imagen desde disco.

    Args:
        file_path: Ruta absoluta al archivo de imagen.

    Returns:
        np.ndarray: Imagen en formato BGR (OpenCV).

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si la imagen no pudo cargarse.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Imagen no encontrada: {file_path}")

    img = cv2.imread(str(path))
    if img is None:
        raise ValueError(f"No se pudo leer la imagen: {file_path}")

    logger.debug(f"Imagen cargada: {path.name} | shape={img.shape}")
    return img


def to_grayscale(img: np.ndarray) -> np.ndarray:
    """
    Convierte imagen BGR a escala de grises.
    Si ya es gris (2D), la retorna sin cambios.
    """
    if len(img.shape) == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def denoise(img: np.ndarray) -> np.ndarray:
    """
    Elimina ruido de la imagen usando filtro No-Local Means.
    Recomendado para imágenes escaneadas con ruido de fondo.
    """
    return cv2.fastNlMeansDenoising(img, h=10, templateWindowSize=7, searchWindowSize=21)


def binarize(img: np.ndarray, method: str = "adaptive") -> np.ndarray:
    """
    Binariza (blanco/negro) la imagen para mejorar el contraste del texto.

    Args:
        img: Imagen en escala de grises.
        method: 'adaptive' (recomendado para variaciones de iluminación)
                'otsu'     (bueno para imágenes con iluminación uniforme)

    Returns:
        Imagen binarizada.
    """
    if method == "adaptive":
        return cv2.adaptiveThreshold(
            img, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=31,
            C=10
        )
    elif method == "otsu":
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
    else:
        raise ValueError(f"Método de binarización no soportado: {method}")


def deskew(img: np.ndarray) -> np.ndarray:
    """
    Detecta y corrige la inclinación (skew) de un documento escaneado.
    Usa Hough Lines para detectar el ángulo de inclinación dominante.

    Args:
        img: Imagen en escala de grises o binarizada.

    Returns:
        Imagen corregida. Si no detecta inclinación, devuelve la original.
    """
    edges = cv2.Canny(img, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                             minLineLength=100, maxLineGap=10)

    if lines is None:
        logger.debug("Deskew: no se detectaron líneas, imagen sin cambios.")
        return img

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 != x1:
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            angles.append(angle)

    if not angles:
        return img

    median_angle = np.median(angles)

    # Solo corregir si la inclinación es significativa (>0.5°) y menor de 45°
    if abs(median_angle) < 0.5 or abs(median_angle) > 45:
        logger.debug(f"Deskew: ángulo {median_angle:.2f}° — sin corrección.")
        return img

    logger.debug(f"Deskew: corrigiendo ángulo de {median_angle:.2f}°")
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h),
                              flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)
    return rotated


def upscale_if_needed(img: np.ndarray, min_width: int = 1000) -> np.ndarray:
    """
    Aumenta el tamaño de la imagen si es demasiado pequeña.
    El OCR tiene mejor desempeño con imágenes de al menos 1000px de ancho.

    Args:
        img: Imagen en cualquier formato.
        min_width: Ancho mínimo deseado en píxeles.

    Returns:
        Imagen escalada o la original si ya es suficientemente grande.
    """
    h, w = img.shape[:2]
    if w >= min_width:
        return img

    scale = min_width / w
    new_w = int(w * scale)
    new_h = int(h * scale)
    logger.debug(f"Upscale: {w}x{h} → {new_w}x{new_h}")
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)


def sharpen(img: np.ndarray) -> np.ndarray:
    """
    Aplica un filtro de nitidez (sharpening) para resaltar bordes del texto.
    """
    kernel = np.array([
        [0, -1,  0],
        [-1, 5, -1],
        [0, -1,  0]
    ])
    return cv2.filter2D(img, -1, kernel)


def full_preprocess(img: np.ndarray, deskew_enabled: bool = True) -> np.ndarray:
    """
    Pipeline completo de preprocesamiento.

    Pasos:
        1. Escala de grises
        2. Upscale si es necesario
        3. Denoise
        4. Deskew (opcional)
        5. Binarización adaptativa
        6. Nitidez

    Args:
        img: Imagen BGR original.
        deskew_enabled: Si True, corrige inclinación.

    Returns:
        Imagen lista para OCR (np.ndarray en escala de grises binarizada).
    """
    gray = to_grayscale(img)
    gray = upscale_if_needed(gray)
    gray = denoise(gray)
    if deskew_enabled:
        gray = deskew(gray)
    binary = binarize(gray, method="adaptive")
    sharp = sharpen(binary)
    return sharp


def image_to_bytes(img: np.ndarray, ext: str = ".png") -> bytes:
    """
    Convierte un np.ndarray a bytes para enviarlo en memoria sin guardar a disco.

    Args:
        img: Imagen procesada.
        ext: Extensión del formato de salida (.png recomendado para OCR).

    Returns:
        bytes: Imagen codificada.
    """
    success, buffer = cv2.imencode(ext, img)
    if not success:
        raise RuntimeError("Error al codificar imagen a bytes.")
    return buffer.tobytes()