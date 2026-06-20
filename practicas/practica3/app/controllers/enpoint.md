# SmartInvoice — Documentación de Endpoints API

> Todos los endpoints protegidos requieren header:
> `Authorization: Bearer <token>`
> Base URL: `http://localhost:8000`

---

## Índice

- [AUTH](#auth)
- [INVOICES — Flujo principal](#invoices--flujo-principal)
- [PROVIDERS — CRUD](#providers--crud)
- [LOGS — Bitácora](#logs--bitácora)
- [DASHBOARD](#dashboard)

---

## AUTH

### `POST /auth/login`

Autentica al usuario y devuelve el token JWT.

**Requiere auth:** No

**Body:**
```json
{
  "username": "admin",
  "password": "mi_password"
}
```

**Respuesta 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJBRE1JTiIsImV4cCI6MTc4MTk1NjAzMn0.9k4WZ7bIyh80LdcPf2OGe-id1PZbhfLifUtonPvEjUQ",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@gmail.com",
    "role": "ADMIN"
  }
}
```

**Errores:**
| Código | Cuándo |
|---|---|
| 401 | Usuario o contraseña incorrectos |
| 403 | Usuario inactivo |

---

### `POST /auth/register`

Crea un nuevo usuario. Solo accesible por ADMIN.

**Requiere auth:** Sí (ADMIN)

**Body:**
```json
{
  "username": "empleado2",
  "email": "emp2@empresa.com",
  "password": "password123",
  "role": "EMPLOYEE"
}
```

**Respuesta 201:**
```json
{
  "id": 3,
  "username": "empleado2",
  "email": "emp2@empresa.com",
  "role": "EMPLOYEE"
}
```

**Errores:**
| Código | Cuándo |
|---|---|
| 409 | El username ya existe |
| 403 | El usuario autenticado no es ADMIN |

---

### `GET /auth/me`

Retorna los datos del usuario autenticado actualmente.

**Requiere auth:** Sí

**Body:** Ninguno

**Respuesta 200:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@test.com",
  "role": "ADMIN",
  "is_active": true
}
```

---

## INVOICES — Flujo principal

### `POST /invoices/upload`

**Paso 2, 3, 4, 5 del flujo.**
Recibe el archivo de factura, corre el OCR y valida los datos extraídos.

**Requiere auth:** Sí

**Content-Type:** `multipart/form-data`

**Body (form-data):**
| Campo | Tipo | Descripción |
|---|---|---|
| `file` | File | Archivo PDF, JPG, JPEG o PNG. Máximo 10MB. |

**Ejemplo curl:**
```bash
curl -X POST http://localhost:8000/invoices/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@factura.pdf"
```

**Respuesta 200 — status: READY** (OCR y validación correctos):
```json
{
  "status": "READY",
  "message": "Factura procesada y validada. Lista para registrar.",
  "file_path": "/app/uploads/abc123.pdf",
  "extracted_data": {
    "invoice_number": "001-2024",
    "date": "2024-01-15",
    "provider": "Distribuidora XYZ S.A.",
    "nit": "1234567-8",
    "subtotal": 1339.29,
    "taxes": 160.71,
    "total": 1500.00,
    "is_duplicate": false
  },
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  },
  "confidence": {
    "invoice_number": true,
    "date": true,
    "provider": true,
    "nit": true,
    "subtotal": true,
    "taxes": true,
    "total": true
  },
  "processing_time_ms": 1240.5
}
```

**Respuesta 200 — status: NEEDS_REVIEW** (Faltan campos o validación falla):
```json
{
  "status": "NEEDS_REVIEW",
  "message": "Algunos campos requieren revisión o corrección.",
  "file_path": "/app/uploads/abc123.pdf",
  "extracted_data": {
    "invoice_number": "001-2024",
    "date": "2024-01-15",
    "provider": "Distribuidora XYZ S.A.",
    "nit": null,
    "subtotal": 1339.29,
    "taxes": null,
    "total": 1500.00
  },
  "validation": {
    "is_valid": false,
    "errors": [
      { "field": "nit", "message": "NIT es obligatorio." },
      { "field": "taxes", "message": "Impuestos es obligatorio." }
    ],
    "warnings": []
  },
  "confidence": { "nit": false, "taxes": false, ... },
  "processing_time_ms": 980.3
}
```

**Respuesta 200 — status: ERROR** (Fallo técnico del OCR):
```json
{
  "status": "ERROR",
  "message": "Error procesando el archivo: No se pudo decodificar la imagen.",
  "file_path": "/app/uploads/abc123.pdf",
  "extracted_data": null,
  "validation": null
}
```

**Errores HTTP:**
| Código | Cuándo |
|---|---|
| 400 | Extensión de archivo no soportada |
| 413 | Archivo mayor a 10MB |
| 401 | Sin token o token inválido |

> **Qué hace el frontend con cada status:**
> - `READY` → Llama a `POST /invoices/trigger-rpa` con los datos recibidos
> - `NEEDS_REVIEW` → Muestra el formulario editable con los datos prellenados e imagen al lado. Cuando el empleado corrige y aprueba, llama a `POST /invoices/validate` y luego a `POST /invoices/trigger-rpa`
> - `ERROR` → Muestra mensaje de error y permite volver a subir

---

### `POST /invoices/validate`

**Paso 5b del flujo (corrección manual).**
El empleado corrigió los datos en el formulario. Valida los datos corregidos antes del RPA.

**Requiere auth:** Sí

**Body:**
```json
{
  "invoice_number": "001-2024",
  "date": "2024-01-15",
  "provider": "Distribuidora XYZ S.A.",
  "nit": "1234567-8",
  "subtotal": 1339.29,
  "taxes": 160.71,
  "total": 1500.00
}
```

**Respuesta 200 — Validación exitosa:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": ["La fecha 2024-01-15 es muy antigua (más de 10 años)."],
  "clean_data": {
    "invoice_number": "001-2024",
    "date": "2024-01-15",
    "provider": "Distribuidora XYZ S.A.",
    "nit": "1234567-8",
    "subtotal": 1339.29,
    "taxes": 160.71,
    "total": 1500.00,
    "is_duplicate": false
  }
}
```

**Respuesta 200 — Validación fallida:**
```json
{
  "is_valid": false,
  "errors": [
    { "field": "nit", "message": "NIT '12345' no tiene formato válido. Formatos aceptados: 1234567-8, 12345678-K, CF." },
    { "field": "total", "message": "total debe ser un número válido (recibido: 'abc')." }
  ],
  "warnings": [],
  "clean_data": null
}
```

> Si `is_valid: true`, el frontend llama a `POST /invoices/trigger-rpa` con el `clean_data` de esta respuesta.

---

### `POST /invoices/trigger-rpa`

**Paso 6, 7, 8 del flujo.**
Dispara el bot Selenium, que llena `/rpa-form`, hace submit, y el backend guarda en DB y crea la bitácora.

**Requiere auth:** Sí

**Body:**
```json
{
  "invoice_data": {
    "invoice_number": "001-2024",
    "date": "2024-01-15",
    "provider": "Distribuidora XYZ S.A.",
    "nit": "1234567-8",
    "subtotal": 1339.29,
    "taxes": 160.71,
    "total": 1500.00,
    "is_duplicate": false
  },
  "file_path": "/app/uploads/abc123.pdf"
}
```

**Respuesta 200 — RPA exitoso:**
```json
{
  "success": true,
  "invoice_id": 42,
  "rpa_status": "SUCCESS",
  "rpa_message": "Factura procesada correctamente. ID: 42",
  "duration_ms": 8340.5
}
```

**Respuesta 200 — RPA fallido (factura guardada como ERROR):**
```json
{
  "success": false,
  "invoice_id": 43,
  "rpa_status": "FAILED",
  "rpa_message": "Timeout: el formulario no cargó a tiempo.",
  "duration_ms": 15000.0
}
```

**Errores HTTP:**
| Código | Cuándo |
|---|---|
| 422 | Los datos no pasan la validación final (double-check) |
| 401 | Sin token |

> **Nota:** El RPA puede tardar entre 5 y 20 segundos. El frontend debe mostrar un estado de "Procesando..." mientras espera esta respuesta.

---

### `POST /invoices/rpa-submit`

**Endpoint interno — llamado por el formulario React, NO por el empleado.**
Recibe el submit del bot Selenium, guarda en DB y crea la bitácora.

**Requiere auth:** No (valida `rpa_token` interno)

**Body:**
```json
{
  "rpa_token": "smartinvoice-rpa-secret-2024",
  "invoice_number": "001-2024",
  "date": "2024-01-15",
  "provider": "Distribuidora XYZ S.A.",
  "nit": "1234567-8",
  "subtotal": "1339.29",
  "taxes": "160.71",
  "total": "1500.00",
  "file_path": "/app/uploads/abc123.pdf",
  "user_id": "1"
}
```

**Respuesta 200:**
```json
{
  "status": "ok",
  "invoice_id": 42,
  "message": "Factura procesada correctamente. ID: 42"
}
```

**Errores HTTP:**
| Código | Cuándo |
|---|---|
| 403 | Token RPA inválido |
| 500 | Error interno al guardar en DB |

---

### `GET /invoices`

Lista todas las facturas. Solo ADMIN puede ver todas; EMPLOYEE ve solo las suyas.

**Requiere auth:** Sí

**Query params opcionales:**
| Param | Tipo | Descripción |
|---|---|---|
| `status` | string | Filtrar por: PENDING, PROCESSED, ERROR, REJECTED |
| `page` | int | Página (default: 1) |
| `limit` | int | Resultados por página (default: 20) |

**Respuesta 200:**
```json
[
  {
    "id": 42,
    "invoice_number": "001-2024",
    "date": "2024-01-15",
    "nit": "1234567-8",
    "subtotal": 1339.29,
    "taxes": 160.71,
    "total": 1500.00,
    "status": "PROCESSED",
    "is_duplicate": false,
    "file_path": "/app/uploads/abc123.pdf",
    "provider_id": 5,
    "user_id": 1,
    "created_at": "2024-01-15 10:30:00"
  }
]
```

---

### `GET /invoices/{id}`

Retorna el detalle de una factura por ID.

**Requiere auth:** Sí

**Path param:** `id` — ID de la factura.

**Respuesta 200:** Mismo objeto que en la lista.

**Errores:**
| Código | Cuándo |
|---|---|
| 404 | Factura no encontrada |

---

### `GET /invoices/{id}/logs`

Retorna la bitácora completa de una factura específica.

**Requiere auth:** Sí

**Respuesta 200:**
```json
[
  {
    "id": 1,
    "invoice_id": 42,
    "user_id": 1,
    "process_date": "2024-01-15 10:30:00",
    "status": "PROCESSED",
    "rpa_result": "SUCCESS",
    "message": "Factura registrada mediante automatización RPA."
  }
]
```

---

## PROVIDERS — CRUD

### `GET /providers`

Lista todos los proveedores.

**Requiere auth:** Sí

**Respuesta 200:**
```json
[
  {
    "id": 1,
    "name": "Distribuidora XYZ S.A.",
    "nit": "1234567-8",
    "address": "6a Avenida 2-34, Zona 1, Guatemala",
    "phone": "22223333",
    "created_at": "2024-01-01 08:00:00"
  }
]
```

---

### `GET /providers/{id}`

Retorna un proveedor por ID.

**Requiere auth:** Sí

**Errores:**
| Código | Cuándo |
|---|---|
| 404 | Proveedor no encontrado |

---

### `POST /providers`

Crea un nuevo proveedor.

**Requiere auth:** Sí (ADMIN)

**Body:**
```json
{
  "name": "Papelería Central S.A.",
  "nit": "7654321-0",
  "address": "3a Calle 5-12, Zona 4",
  "phone": "55556666"
}
```

**Respuesta 201:**
```json
{
  "id": 6,
  "name": "Papelería Central S.A.",
  "nit": "7654321-0",
  "address": "3a Calle 5-12, Zona 4",
  "phone": "55556666",
  "created_at": "2024-01-15 10:45:00"
}
```

**Errores:**
| Código | Cuándo |
|---|---|
| 409 | Ya existe un proveedor con ese NIT |
| 422 | NIT con formato inválido o nombre vacío |

---

### `PUT /providers/{id}`

Actualiza un proveedor existente. Solo los campos enviados se actualizan.

**Requiere auth:** Sí (ADMIN)

**Body (todos opcionales):**
```json
{
  "name": "Papelería Central de Guatemala S.A.",
  "address": "3a Calle 5-12, Zona 4, Local 2",
  "phone": "44447777"
}
```

**Respuesta 200:** Objeto proveedor actualizado.

**Errores:**
| Código | Cuándo |
|---|---|
| 404 | Proveedor no encontrado |
| 409 | El NIT nuevo ya pertenece a otro proveedor |

---

### `DELETE /providers/{id}`

Elimina un proveedor.

**Requiere auth:** Sí (ADMIN)

**Respuesta 200:**
```json
{
  "message": "Proveedor ID 6 eliminado correctamente."
}
```

**Errores:**
| Código | Cuándo |
|---|---|
| 404 | Proveedor no encontrado |
| 409 | El proveedor tiene facturas asociadas y no puede eliminarse |

---

## LOGS — Bitácora

### `GET /logs`

Retorna toda la bitácora de procesamiento.

**Requiere auth:** Sí (ADMIN)

**Respuesta 200:**
```json
[
  {
    "id": 1,
    "invoice_id": 42,
    "user_id": 1,
    "process_date": "2024-01-15 10:30:00",
    "status": "PROCESSED",
    "rpa_result": "SUCCESS",
    "message": "Factura registrada mediante automatización RPA."
  },
  {
    "id": 2,
    "invoice_id": 43,
    "user_id": 2,
    "process_date": "2024-01-15 11:00:00",
    "status": "ERROR",
    "rpa_result": "FAILED",
    "message": "Timeout: el formulario no cargó a tiempo."
  }
]
```

---

## DASHBOARD

### `GET /dashboard/metrics`

Métricas generales del sistema para el panel principal.

**Requiere auth:** Sí

**Respuesta 200:**
```json
{
  "total_invoices": 150,
  "processed": 135,
  "pending": 5,
  "with_errors": 7,
  "rejected": 3,
  "duplicates": 4,
  "total_amount": 225000.50,
  "rpa_success_rate": 94.7
}
```

---

### `GET /dashboard/recent`

Últimas 10 facturas procesadas.

**Requiere auth:** Sí

**Query params opcionales:**
| Param | Tipo | Default |
|---|---|---|
| `limit` | int | 10 |

**Respuesta 200:**
```json
[
  {
    "id": 150,
    "invoice_number": "001-2024",
    "status": "PROCESSED",
    "total": 1500.00,
    "is_duplicate": false,
    "created_at": "2024-01-15 10:30:00"
  }
]
```

---

## Flujo completo de llamadas desde el frontend

```
1. POST /auth/login
        └─► Guarda token en localStorage

2. POST /invoices/upload (con el archivo)
        │
        ├── status=READY
        │       └─► POST /invoices/trigger-rpa (con extracted_data + file_path)
        │                   └─► Muestra resultado al empleado
        │
        └── status=NEEDS_REVIEW
                └─► Muestra form editable
                        └─► POST /invoices/validate (con datos corregidos)
                                │
                                ├── is_valid=true
                                │       └─► POST /invoices/trigger-rpa
                                │
                                └── is_valid=false
                                        └─► Vuelve a mostrar errores en el form

3. GET /dashboard/metrics   ← Panel principal
4. GET /invoices            ← Lista de facturas
5. GET /logs                ← Bitácora completa
```