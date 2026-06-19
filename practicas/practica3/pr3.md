Perfecto — ahora sí tenemos un **flujo claro y realista** ✅  
Con eso te voy a dar lo que necesitas:

1. ✅ **Estructura completa del backend (bien organizada con MVC)**
2. ✅ **Dónde van OCR y RPA exactamente**
3. ✅ **Qué hace cada carpeta/archivo**
4. ✅ **Flujo detallado paso a paso (listo para documentación y LLM)**

***

# 🧠 ✅ 1. ESTRUCTURA DEL BACKEND (SIMPLE, LIMPIA Y COMPLETA)

👉 Enfocada en:

* Controllers (endpoints)
* Services (lógica)
* Repositories (DB)
* Módulos separados para OCR y RPA

***

## 📁 Proyecto

```bash
smart-invoice/
│
├── app/
│   ├── main.py
│
│   ├── core/
│   │   ├── config.py          # Variables de entorno
│   │   ├── database.py        # Conexión PostgreSQL
│   │   ├── security.py        # JWT / auth
│
│   ├── models/                # ORM
│   │   ├── user_model.py
│   │   ├── invoice_model.py
│   │   ├── provider_model.py
│   │   ├── log_model.py
│
│   ├── schemas/               # Pydantic (entrada/salida API)
│   │   ├── user_schema.py
│   │   ├── invoice_schema.py
│   │   ├── provider_schema.py
│
│   ├── controllers/           # ENDPOINTS
│   │   ├── auth_controller.py
│   │   ├── invoice_controller.py
│   │   ├── provider_controller.py
│   │   ├── dashboard_controller.py
│
│   ├── services/              # 🔥 LÓGICA DEL NEGOCIO
│   │   ├── auth_service.py
│   │   ├── invoice_service.py
│   │   ├── validation_service.py
│   │   ├── log_service.py
│   │   ├── report_service.py
│   │   ├── email_service.py
│
│   ├── repositories/          # DB
│   │   ├── user_repository.py
│   │   ├── invoice_repository.py
│   │   ├── provider_repository.py
│   │   ├── log_repository.py
│
│   ├── modules/               # INTELIGENCIA Y AUTOMATIZACIÓN
│   │
│   │   ├── ocr/
│   │   │   ├── ocr_engine.py        # Tesseract/EasyOCR
│   │   │   └── ocr_pipeline.py      # flujo OCR completo
│   │
│   │   ├── computer_vision/
│   │   │   ├── preprocess.py        # OpenCV
│   │   │   └── image_utils.py
│   │
│   │   ├── parser/
│   │   │   ├── invoice_parser.py    # regex (CRÍTICO)
│   │   │   └── patterns.py
│   │
│   │   ├── rpa/
│   │   │   ├── rpa_bot.py           # Selenium
│   │   │   └── rpa_service.py       # wrapper del bot
│
│   ├── reports/
│   │   ├── pdf_generator.py
│   │   ├── excel_generator.py
│   │   ├── csv_generator.py
│
```

***

# 📍 ✅ 2. ¿QUÉ VA EN CADA PARTE?

***

## 🎮 CONTROLLERS (ENDPOINTS)

👉 SOLO reciben request y llaman services

Ejemplo:

```python
# invoice_controller.py

@router.post("/upload")
async def upload_invoice(file: UploadFile):
    return await process_invoice(file)
```

***

## 🧠 SERVICES (CEREBRO)

👉 Aquí vive TODO el flujo

Ejemplo:

```python
def process_invoice(file):

    # 1. OCR
    text = ocr_pipeline(file)

    # 2. Extraer datos
    data = parse_invoice(text)

    # 3. Validar
    is_valid, errors = validate_invoice(data)

    if not is_valid:
        return {"status": "error", "data": data, "errors": errors}

    # 4. Guardar en DB
    invoice = save_invoice(data)

    # 5. RPA 🔥
    rpa_result = run_rpa(invoice)

    # 6. Log
    create_log(invoice, rpa_result)

    # 7. Reporte
    report = generate_report(invoice)

    # 8. Email
    send_email(report)

    return invoice
```

***

## 🗄️ REPOSITORIES

👉 SOLO base de datos

***

## 🔍 OCR (modules/ocr)

👉 Solo extracción de texto

```python
def extract_text(image):
    return pytesseract.image_to_string(image)
```

***

## 👁️ COMPUTER VISION

👉 mejora imagen antes del OCR

***

## 🧾 PARSER

👉 convierte texto en datos estructurados

```python
def parse_invoice(text):
    return {
        "numero": ...,
        "nit": ...
    }
```

***

## 🤖 RPA (MUY IMPORTANTE)

***

### 📁 modules/rpa/

```bash
rpa/
├── rpa_bot.py       # Selenium (acciones)
├── rpa_service.py   # integración con sistema
```

***

### 🧠 rpa\_bot.py

```python
from selenium import webdriver

def run_bot(invoice):

    driver = webdriver.Chrome()

    driver.get("http://localhost:5173/rpa-form")

    driver.find_element("name", "numero").send_keys(invoice.numero)
    driver.find_element("name", "total").send_keys(invoice.total)

    driver.find_element("id", "submit").click()

    driver.quit()

    return "SUCCESS"
```

***

### 🧠 rpa\_service.py

👉 capa intermedia

```python
from .rpa_bot import run_bot

def run_rpa(invoice):
    try:
        result = run_bot(invoice)
        return result
    except:
        return "ERROR"
```

***

# 3. FLUJO COMPLETO
***

# FLUJO DETALLADO

***

## 1. AUTENTICACIÓN

El usuario:

* ingresa credenciales
* recibe token JWT
* accede al sistema

***

## 2. CARGA DE FACTURA

El usuario:

* selecciona imagen/PDF
* envía a:

```
POST /invoices/upload
```

***

## 3. PROCESAMIENTO OCR

El sistema:

1. Preprocesa imagen (OpenCV)
2. Ejecuta OCR
3. Obtiene texto

***

## 4. EXTRACCIÓN DE DATOS

El sistema:

* usa regex
* extrae:

```
numero
fecha
proveedor
NIT
subtotal
impuestos
total
```

***

## 5. VALIDACIÓN

Se verifica:

* campos completos
* formato de NIT
* números válidos
* duplicados

***

### Si hay error:

* NO guarda
* devuelve datos al frontend

Frontend:

* muestra formulario editable
* muestra imagen al lado

***

### Si todo está bien:

continúa flujo

***

## 6. RPA (AUTOMATIZACIÓN CLAVE)

El sistema:

1. ejecuta bot Selenium
2. abre:

```
http://localhost:5173/rpa-form
```

3. llena campos automáticamente:

* número
* NIT
* total

4. envía formulario

5. recibe resultado:

* success / error

## 7. GUARDADO

* se guarda en PostgreSQL
* estado = "Procesado"

***

***

## 8. BITÁCORA

Se guarda:

* fecha
* usuario
* factura
* estado RPA
* resultado

***

## 9. REPORTE

Se genera:

* PDF / Excel / CSV

Ejemplo:

```
Factura: 001
Estado: OK
Total: Q1500
```

***

## 10. ENVÍO DE CORREO

Se envía:

* resumen
* archivo adjunto

esto se ejecuta solo cuando se presiona el boton no es automatico

***

## 11. FRONTEND

Tiene 2 vistas importantes:

***

### Vista EMPLEADO

* subir factura
* ver estado
* ver errores

***

### Vista FORM RPA

* formulario simple
* recibe lo llenado por bot

***

# RESUMEN FINAL (CLARIDAD TOTAL)

Tu sistema hace:

```
Factura → OCR → Parser → Validación
         ↓
      (si error → editar)

         ↓
       DB
         ↓
       RPA 
         ↓
  Bitácora + Reporte + Email
```
