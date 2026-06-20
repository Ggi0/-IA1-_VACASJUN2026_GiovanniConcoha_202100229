


dependencias:

```
pip install python-multipart
pip install pydantic
pip install pydantic-settings

pip install sqlalchemy
pip install asyncpg
pip install alembic

pip install python-jose[cryptography]
pip install passlib[bcrypt]

pip install opencv-python-headless
pip install numpy
pip install Pillow

pip install pdf2image
pip install pytesseract
pip install easyocr

pip install reportlab
pip install openpyxl
pip install pandas

pip install selenium
pip install webdriver-manager

pip install python-dotenv
pip install aiofiles
pip install httpx



```






[Empleado sube factura]
        │
        ▼
POST /invoices/upload
        │
        ▼
[OCR Pipeline] → extrae campos
        │
        ├── status=NEEDS_REVIEW ──────────────────────────────────┐
        │                                                          │
        │   [Frontend muestra form editable + imagen]             │
        │   [Empleado corrige y aprueba]                          │
        │   POST /invoices/trigger-rpa (datos corregidos)         │
        │                                                          │
        └── status=READY ──────────────────────────────────────────┤
                                                                   │
                                                                   ▼
                                              POST /invoices/trigger-rpa (datos OCR)
                                                                   │
                                                                   ▼
                                                         [rpa_service.execute_rpa_and_save()]
                                                                   │
                                                                   ▼
                                              [RPABot corre en Thread (no bloquea FastAPI)]
                                                                   │
                                                 ┌─────────────────┴──────────────────┐
                                                 │                                    │
                                                 ▼                                    │
                                    Chromium abre /rpa-form                          │
                                                 │                                   │
                                                 ▼                                   │
                                    Bot llena campos con Selenium                    │
                                                 │                                   │
                                                 ▼                                   │
                                    Bot hace click submit                            │
                                                 │                                   │
                                                 ▼                                   │
                                    React hace fetch POST                            │
                                    /api/invoices/rpa-submit                         │
                                                 │                                   │
                                                 ▼                                   │
                                    Backend guarda en DB ◄───────────────────────────┘
                                    status=PROCESSED
                                                 │
                                                 ▼
                                    Backend crea bitácora
                                                 │
                                                 ▼
                                    React muestra #rpa-result-success
                                                 │
                                                 ▼
                                    Bot lee el DOM → RPABotResult(success=True)
                                                 │
                                                 ▼
                                    rpa_service retorna resultado al controller
                                                 │
                                                 ▼
                                    Respuesta JSON al frontend










Usuario (bot) hace click en #rpa-submit-btn
    │
    ▼
React ejecuta handleSubmit()
    │
    ▼
fetch("POST /api/invoices/rpa-submit", {
    body: JSON.stringify(formData)  ← todos los campos
})
    │
    ▼
Backend valida token, guarda en DB, crea bitácora
    │
    ▼
Response: { status: "ok", invoice_id: 42, message: "Factura procesada. ID: 42" }
    │
    ▼
React renderiza <div id="rpa-result-success">✅ Factura procesada. ID: 42</div>
    │
    ▼
Bot lee el texto → RPABotResult(success=True, invoice_id=42)























[dict invoice_data]  ←─── viene del OCR o del form editado por el empleado
        │
        ▼
POST /invoices/trigger-rpa (HTTP, desde frontend)
        │
        ▼
invoice_controller.trigger_rpa()
        │
        ▼
rpa_service.execute_rpa_and_save(invoice_data, file_path, user_id, db)
        │
        ├─ [Thread] RPABot.fill_and_submit(invoice_data, file_path, user_id)
        │       │
        │       ├─ driver.get("http://frontend:5173/rpa-form")
        │       ├─ fill field-invoice_number = "001-2024"
        │       ├─ fill field-date           = "2024-01-15"
        │       ├─ fill field-provider       = "Distribuidora XYZ S.A."
        │       ├─ fill field-nit            = "1234567-8"
        │       ├─ fill field-subtotal       = "1339.29"
        │       ├─ fill field-taxes          = "160.71"
        │       ├─ fill field-total          = "1500.0"
        │       ├─ fill field-file_path      = "/app/uploads/abc.pdf" (JS)
        │       ├─ fill field-user_id        = "1" (JS)
        │       ├─ fill field-rpa_token      = "smartinvoice-rpa-secret-2024" (JS)
        │       ├─ click #rpa-submit-btn
        │       │
        │       │   [React hace fetch → POST /api/invoices/rpa-submit]
        │       │       │
        │       │       ▼
        │       │   invoice_controller.rpa_form_submit()
        │       │       ├─ Valida rpa_token
        │       │       ├─ provider_repo.get_or_create_by_nit()
        │       │       ├─ invoice_repo.create(status=PROCESSED)
        │       │       ├─ log_repo.create(rpa_result=SUCCESS)
        │       │       └─ return { invoice_id: 42 }
        │       │
        │       │   [React renderiza #rpa-result-success]
        │       │
        │       └─ Bot lee DOM → RPABotResult(success=True, invoice_id=42)
        │
        ├─ rpa_service registra bitácora (si no la registró rpa-submit)
        │
        └─ Retorna { success: true, invoice_id: 42, rpa_status: "SUCCESS" }
                │
                ▼
        invoice_controller retorna response al frontend