"""
rpa_bot.py
==========
Bot Selenium que automatiza el llenado del formulario /rpa-form.

Flujo exacto:
  1. Recibe los datos extraídos por OCR (dict con los campos de la factura)
  2. Abre http://localhost:5173/rpa-form en Chromium headless
  3. Espera a que el formulario esté disponible en el DOM
  4. Llena cada campo usando los IDs definidos en RpaForm.tsx
  5. Hace click en el botón de submit
  6. Espera el resultado (elemento #rpa-result-success o #rpa-result-error)
  7. Retorna RPABotResult con el estado final

IMPORTANTE:
  - El bot corre en modo headless dentro del contenedor Docker.
  - Usa Chromium (ya instalado en el Dockerfile con chromium + chromium-driver).
  - El RPA token es un secret compartido entre el bot y el backend FastAPI.
    El backend valida ese token en POST /api/invoices/rpa-submit para evitar
    que cualquier cliente externo pueda hacer submit directamente.
"""

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────

# URL base del frontend React (dentro de Docker Compose, el frontend
# está en el servicio "frontend" en el puerto 5173 o 80 según config)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://frontend:5173")
RPA_FORM_PATH = "/rpa-form"

# Token interno para validar que el submit vino del bot y no de un cliente externo
RPA_SECRET_TOKEN = os.getenv("RPA_SECRET_TOKEN", "smartinvoice-rpa-secret-2024")

# Timeouts
WAIT_FOR_FORM_SECONDS = 15    # Tiempo máximo esperando que cargue el formulario
WAIT_FOR_RESULT_SECONDS = 20  # Tiempo máximo esperando el resultado del submit

# IDs de los elementos HTML en RpaForm.tsx
FIELD_IDS = {
    "invoice_number": "field-invoice_number",
    "date":           "field-date",
    "provider":       "field-provider",
    "nit":            "field-nit",
    "subtotal":       "field-subtotal",
    "taxes":          "field-taxes",
    "total":          "field-total",
    "file_path":      "field-file_path",
    "user_id":        "field-user_id",
    "rpa_token":      "field-rpa_token",
}

SUBMIT_BTN_ID = "rpa-submit-btn"
RESULT_SUCCESS_ID = "rpa-result-success"
RESULT_ERROR_ID = "rpa-result-error"


# ─────────────────────────────────────────────────────────────────
# DATACLASS DE RESULTADO
# ─────────────────────────────────────────────────────────────────

@dataclass
class RPABotResult:
    """
    Resultado que el bot devuelve al rpa_service.
    rpa_service lo usa para decidir el estado de la bitácora.
    """
    success: bool
    message: str                     # Mensaje del frontend o error interno
    invoice_id: Optional[int] = None # ID asignado por la DB (si el backend lo devuelve)
    duration_ms: float = 0.0
    error_type: Optional[str] = None # "TIMEOUT" | "ELEMENT_NOT_FOUND" | "SUBMIT_ERROR" | None


# ─────────────────────────────────────────────────────────────────
# BOT PRINCIPAL
# ─────────────────────────────────────────────────────────────────

class RPABot:
    """
    Bot Selenium para el llenado automatizado del formulario de facturas.

    Uso (desde rpa_service.py):
        bot = RPABot()
        result = bot.fill_and_submit(invoice_data, file_path, user_id)
        bot.close()

    O usando context manager:
        with RPABot() as bot:
            result = bot.fill_and_submit(invoice_data, file_path, user_id)
    """

    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self._init_driver()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ─────────────────────────────────────────────
    # Inicialización del WebDriver
    # ─────────────────────────────────────────────

    def _init_driver(self):
        """
        Configura Chromium en modo headless para ejecutar dentro de Docker.
        Los flags están ajustados para entornos sin GUI y sin sandbox
        (necesario en contenedores).
        """
        options = Options()
        options.add_argument("--headless")           # Sin ventana de GUI
        options.add_argument("--no-sandbox")          # Requerido en Docker
        options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memoria compartida
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280,800")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")

        # Ruta al chromedriver instalado en el Dockerfile
        # En el Dockerfile: apt-get install -y chromium chromium-driver
        chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
        service = Service(executable_path=chromedriver_path)

        try:
            self.driver = webdriver.Chrome(service=service, options=options)
            logger.info("RPABot: Chromium iniciado correctamente.")
        except WebDriverException as e:
            logger.error(f"RPABot: No se pudo iniciar Chromium: {e}")
            raise

    # ─────────────────────────────────────────────
    # API pública
    # ─────────────────────────────────────────────

    def fill_and_submit(
        self,
        invoice_data: dict,
        file_path: str,
        user_id: int,
    ) -> RPABotResult:
        """
        Flujo completo del RPA:
            1. Navega al formulario
            2. Llena todos los campos
            3. Hace submit
            4. Espera y retorna el resultado

        Args:
            invoice_data: dict con los campos de la factura.
                          Claves esperadas: invoice_number, date, provider,
                          nit, subtotal, taxes, total.
            file_path:    Ruta del archivo guardado en disco (para la DB).
            user_id:      ID del usuario que procesó la factura.

        Returns:
            RPABotResult con success=True/False y el mensaje del servidor.
        """
        start = time.monotonic()

        try:
            # Paso 1: Navegar al formulario
            form_url = f"{FRONTEND_URL}{RPA_FORM_PATH}"
            logger.info(f"RPABot: Navegando a {form_url}")
            self.driver.get(form_url)

            # Paso 2: Esperar a que el formulario esté visible
            self._wait_for_element(SUBMIT_BTN_ID)
            logger.info("RPABot: Formulario cargado.")

            # Paso 3: Preparar datos a llenar (incluyendo campos ocultos)
            all_fields = {
                **invoice_data,
                "file_path":  file_path,
                "user_id":    str(user_id),
                "rpa_token":  RPA_SECRET_TOKEN,
            }

            # Paso 4: Llenar cada campo
            for field_key, element_id in FIELD_IDS.items():
                value = str(all_fields.get(field_key, "") or "")
                self._fill_field(element_id, value)

            logger.info("RPABot: Campos llenados. Haciendo submit...")

            # Paso 5: Click en submit
            submit_btn = self.driver.find_element(By.ID, SUBMIT_BTN_ID)
            submit_btn.click()

            # Paso 6: Esperar resultado
            result = self._wait_for_result()
            result.duration_ms = round((time.monotonic() - start) * 1000, 2)
            return result

        except TimeoutException as e:
            logger.error(f"RPABot: Timeout esperando elemento: {e}")
            return RPABotResult(
                success=False,
                message="Timeout: el formulario o el resultado no cargó a tiempo.",
                duration_ms=round((time.monotonic() - start) * 1000, 2),
                error_type="TIMEOUT",
            )
        except NoSuchElementException as e:
            logger.error(f"RPABot: Elemento no encontrado: {e}")
            return RPABotResult(
                success=False,
                message=f"Elemento no encontrado en el formulario: {e.msg}",
                duration_ms=round((time.monotonic() - start) * 1000, 2),
                error_type="ELEMENT_NOT_FOUND",
            )
        except Exception as e:
            logger.error(f"RPABot: Error inesperado: {e}", exc_info=True)
            return RPABotResult(
                success=False,
                message=f"Error interno del bot: {str(e)}",
                duration_ms=round((time.monotonic() - start) * 1000, 2),
                error_type="INTERNAL_ERROR",
            )

    def close(self):
        """Cierra el navegador y libera recursos."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("RPABot: Chromium cerrado.")
            except Exception as e:
                logger.warning(f"RPABot: Error al cerrar Chromium: {e}")
            finally:
                self.driver = None

    # ─────────────────────────────────────────────
    # Helpers privados
    # ─────────────────────────────────────────────

    def _wait_for_element(self, element_id: str, timeout: int = WAIT_FOR_FORM_SECONDS):
        """Espera hasta que un elemento con el ID dado sea visible en el DOM."""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.ID, element_id))
        )

    def _fill_field(self, element_id: str, value: str):
        """
        Limpia un campo y escribe el valor.
        Funciona tanto para inputs visibles como hidden.
        Para campos hidden usa JavaScript porque Selenium no puede
        interactuar directamente con elementos ocultos.
        """
        try:
            element = self.driver.find_element(By.ID, element_id)
            input_type = element.get_attribute("type")

            if input_type == "hidden":
                # Usar JS para campos ocultos
                self.driver.execute_script(
                    "arguments[0].value = arguments[1];", element, value
                )
            else:
                element.clear()
                element.send_keys(value)

            logger.debug(f"RPABot: Campo '{element_id}' = '{value}'")

        except NoSuchElementException:
            logger.warning(f"RPABot: Campo '{element_id}' no encontrado. Omitiendo.")

    def _wait_for_result(self) -> RPABotResult:
        """
        Espera a que aparezca en el DOM el div de resultado
        (#rpa-result-success o #rpa-result-error).

        El componente React renderiza uno de estos divs después
        de que el fetch al backend completa.
        """
        wait = WebDriverWait(self.driver, WAIT_FOR_RESULT_SECONDS)

        try:
            # Esperar cualquiera de los dos elementos de resultado
            result_element = wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, RESULT_SUCCESS_ID)),
                    EC.presence_of_element_located((By.ID, RESULT_ERROR_ID)),
                )
            )
        except TimeoutException:
            raise TimeoutException("El resultado del formulario no apareció en el DOM.")

        # Determinar cuál apareció
        try:
            success_el = self.driver.find_element(By.ID, RESULT_SUCCESS_ID)
            message = success_el.text.strip()

            # Intentar extraer el invoice_id del mensaje
            # El React pone: "Factura procesada correctamente. ID: 42"
            invoice_id = None
            if "ID:" in message:
                try:
                    invoice_id = int(message.split("ID:")[-1].strip().split()[0])
                except (ValueError, IndexError):
                    pass

            logger.info(f"RPABot: Submit exitoso. Mensaje: '{message}'")
            return RPABotResult(success=True, message=message, invoice_id=invoice_id)

        except NoSuchElementException:
            pass

        try:
            error_el = self.driver.find_element(By.ID, RESULT_ERROR_ID)
            message = error_el.text.strip()
            logger.warning(f"RPABot: Submit con error. Mensaje: '{message}'")
            return RPABotResult(
                success=False,
                message=message,
                error_type="SUBMIT_ERROR",
            )
        except NoSuchElementException:
            pass

        return RPABotResult(
            success=False,
            message="No se encontró elemento de resultado en el DOM.",
            error_type="ELEMENT_NOT_FOUND",
        )