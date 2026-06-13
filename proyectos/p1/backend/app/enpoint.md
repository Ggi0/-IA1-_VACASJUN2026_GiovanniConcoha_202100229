# Doctor Byte — Contrato de Endpoints

Base URL: `http://localhost:8000/api`

Todos los endpoints retornan `Content-Type: application/json`.
Los errores siguen el formato:
```json
{ "error": "Descripción del error" }
```

---

## 1. USUARIO — Diagnóstico

### POST /diagnosticar  - probado 1,2,3 diagnosticos
Envía síntomas seleccionados y obtiene diagnósticos + recomendaciones.
También guarda el resultado en el historial y notifica por Telegram.

**Request:**
```json
{
  "sintomas": ["S01", "S03", "S11"],
  "usuario": "Juan Pérez"          // opcional, para el historial
}
```

**Response 200:**
```json
{
  "diagnosticos": [
    {
      "falla_id": "F02",
      "nombre": "Sobrecalentamiento del sistema",
      "tipo": "Hardware",
      "descripcion": "El equipo presenta temperaturas excesivas...",
      "recomendaciones": [
        "Limpiar ventiladores internos...",
        "Revisar que la pasta térmica..."
      ]
    }
  ],
  "historial_id": "uuid-generado",
  "telegram_enviado": true
}
```

**Response 200 (sin diagnóstico):**
```json
{
  "diagnosticos": [],
  "mensaje": "No se encontró un diagnóstico para los síntomas seleccionados.",
  "historial_id": "uuid-generado",
  "telegram_enviado": false
}
```

**Response 400:**
```json
{ "error": "Debe seleccionar al menos un síntoma." }
```

---

### GET /sintomas - probado
Lista todos los síntomas disponibles para mostrar al usuario.

**Response 200:**
```json
{
  "sintomas": [
    { "id": "S01", "nombre": "Pantalla negra al encender", "descripcion": "..." },
    { "id": "S02", "nombre": "Pitidos al arrancar", "descripcion": "..." }
  ]
}
```

---

### GET /historial  - porbado 
Lista todos los diagnósticos realizados (más recientes primero).

**Query params:** `?limit=20&offset=0`

**Response 200:**
```json
{
  "total": 45,
  "historial": [
    {
      "id": "uuid",
      "fecha": "2025-06-10T14:32:00",
      "usuario": "Juan Pérez",
      "sintomas_seleccionados": ["S01", "S03", "S11"],
      "diagnosticos": [
        {
          "falla_id": "F02",
          "nombre": "Sobrecalentamiento del sistema",
          "tipo": "Hardware",
          "descripcion": "...",
          "recomendaciones": ["..."]
        }
      ]
    }
  ]
}
```

---

### GET /historial/{id}  - probado
Detalle de un diagnóstico específico del historial.

**Response 200:**
```json
{
  "id": "uuid",
  "fecha": "2025-06-10T14:32:00",
  "usuario": "Juan Pérez",
  "sintomas_seleccionados": ["S01", "S03", "S11"],
  "diagnosticos": [...]
}
```

**Response 404:**
```json
{ "error": "Historial no encontrado." }
```

---

## 2. ADMINISTRADOR — CRUD Síntomas

### GET /admin/sintomas
Lista todos los síntomas.

**Response 200:**
```json
{
  "sintomas": [
    { "id": "S01", "nombre": "Pantalla negra al encender", "descripcion": "..." }
  ]
}
```

---

### POST /admin/sintomas
Agrega un nuevo síntoma a la base de conocimiento Prolog.

**Request:**
```json
{
  "id": "S21",
  "nombre": "Monitor parpadeante",
  "descripcion": "La imagen del monitor parpadea constantemente."
}
```

**Response 201:**
```json
{
  "mensaje": "Síntoma S21 agregado correctamente.",
  "sintoma": { "id": "S21", "nombre": "Monitor parpadeante", "descripcion": "..." }
}
```

**Response 409 (ID duplicado):**
```json
{ "error": "Ya existe un síntoma con el ID S21." }
```

---

### PUT /admin/sintomas/{id}
Actualiza un síntoma existente (elimina y re-agrega).

**Request:**
```json
{
  "nombre": "Monitor parpadeante o con líneas",
  "descripcion": "Descripción actualizada."
}
```

**Response 200:**
```json
{
  "mensaje": "Síntoma S21 actualizado correctamente.",
  "sintoma": { "id": "S21", "nombre": "Monitor parpadeante o con líneas", "descripcion": "..." }
}
```

**Response 404:**
```json
{ "error": "Síntoma S21 no encontrado." }
```

---

### DELETE /admin/sintomas/{id}
Elimina un síntoma de la base de conocimiento.

**Response 200:**
```json
{ "mensaje": "Síntoma S21 eliminado correctamente." }
```

**Response 404:**
```json
{ "error": "Síntoma S21 no encontrado." }
```

---

## 3. ADMINISTRADOR — CRUD Fallas

### GET /admin/fallas
Lista todas las fallas diagnosticables.

**Response 200:**
```json
{
  "fallas": [
    { "id": "F01", "nombre": "Memoria RAM defectuosa", "tipo": "Hardware", "descripcion": "..." }
  ]
}
```

---

### POST /admin/fallas
Agrega una nueva falla.

**Request:**
```json
{
  "id": "F13",
  "nombre": "Fallo de batería CMOS",
  "tipo": "Hardware",
  "descripcion": "La batería de la placa base está agotada."
}
```

**Response 201:**
```json
{
  "mensaje": "Falla F13 agregada correctamente.",
  "falla": { "id": "F13", "nombre": "Fallo de batería CMOS", "tipo": "Hardware", "descripcion": "..." }
}
```

---

### PUT /admin/fallas/{id}
Actualiza una falla existente.

**Request:**
```json
{
  "nombre": "Fallo de batería CMOS o RTC",
  "tipo": "Hardware",
  "descripcion": "Descripción actualizada."
}
```

**Response 200:**
```json
{ "mensaje": "Falla F13 actualizada correctamente.", "falla": { ... } }
```

---

### DELETE /admin/fallas/{id}
Elimina una falla. Advertencia: también debería eliminarse sus reglas asociadas.

**Response 200:**
```json
{ "mensaje": "Falla F13 eliminada correctamente." }
```

---

## 4. ADMINISTRADOR — CRUD Recomendaciones

### GET /admin/recomendaciones
Lista todas las recomendaciones.

**Response 200:**
```json
{
  "recomendaciones": [
    { "id": "R01", "falla_id": "F01", "descripcion": "Apagar el equipo, retirar los módulos RAM..." }
  ]
}
```

---

### GET /admin/recomendaciones?falla_id=F01
Filtra recomendaciones por falla.

**Response 200:**
```json
{
  "recomendaciones": [
    { "id": "R01", "falla_id": "F01", "descripcion": "..." },
    { "id": "R02", "falla_id": "F01", "descripcion": "..." }
  ]
}
```

---

### POST /admin/recomendaciones
Agrega una nueva recomendación.

**Request:**
```json
{
  "id": "R16",
  "falla_id": "F13",
  "descripcion": "Reemplazar la batería CMOS de la placa base (CR2032)."
}
```

**Response 201:**
```json
{
  "mensaje": "Recomendación R16 agregada correctamente.",
  "recomendacion": { "id": "R16", "falla_id": "F13", "descripcion": "..." }
}
```

---

### PUT /admin/recomendaciones/{id}
Actualiza una recomendación existente.

**Request:**
```json
{
  "falla_id": "F13",
  "descripcion": "Descripción actualizada."
}
```

**Response 200:**
```json
{ "mensaje": "Recomendación R16 actualizada correctamente.", "recomendacion": { ... } }
```

---

### DELETE /admin/recomendaciones/{id}

**Response 200:**
```json
{ "mensaje": "Recomendación R16 eliminada correctamente." }
```

---

## 5. ADMINISTRADOR — Gestión de Reglas (Asociación síntoma ↔ falla)

### GET /admin/reglas
Lista todas las reglas de diagnóstico.

**Response 200:**
```json
{
  "reglas": [
    { "falla_id": "F01", "sintomas": ["S02"] },
    { "falla_id": "F01", "sintomas": ["S01", "S17"] },
    { "falla_id": "F02", "sintomas": ["S03", "S11"] }
  ]
}
```

---

### POST /admin/reglas
Agrega una nueva regla: asocia una lista de síntomas a una falla.
Una lista de 1 síntoma = diagnóstico por síntoma único.
Una lista de 2 o 3 síntomas = diagnóstico combinado.

**Request:**
```json
{
  "falla_id": "F13",
  "sintomas": ["S01", "S03"]
}
```

**Response 201:**
```json
{
  "mensaje": "Regla agregada correctamente: F13 ← [S01, S03]",
  "regla": { "falla_id": "F13", "sintomas": ["S01", "S03"] }
}
```

**Response 400 (falla o síntoma no existen):**
```json
{ "error": "La falla F13 no existe. Créela primero." }
```

**Response 409 (regla duplicada):**
```json
{ "error": "Ya existe una regla F13 ← [S01, S03]." }
```

---

### DELETE /admin/reglas
Elimina una regla específica.

**Request:**
```json
{
  "falla_id": "F13",
  "sintomas": ["S01", "S03"]
}
```

**Response 200:**
```json
{ "mensaje": "Regla F13 ← [S01, S03] eliminada correctamente." }
```

**Response 404:**
```json
{ "error": "La regla especificada no existe." }
```