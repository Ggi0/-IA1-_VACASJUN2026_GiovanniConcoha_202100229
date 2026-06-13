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

