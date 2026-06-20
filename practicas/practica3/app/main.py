"""
main.py
=======
Punto de entrada de la aplicación FastAPI.
Registra todos los routers del proyecto.

Para correr localmente:
    uvicorn app.main:app --reload --port 8000

Documentación interactiva:
    http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import test_connection

# ── Routers ─────────────────────────────────────────────────────
from app.controllers.auth_controller      import router as auth_router
from app.controllers.invoice_controller   import router as invoice_router
from app.controllers.provider_controller  import router as provider_router
from app.controllers.log_controller       import router as log_router
from app.controllers.dashboard_controller import router as dashboard_router

# ── App ─────────────────────────────────────────────────────────
app = FastAPI(
    title="SmartInvoice — Práctica 3",
    description="Sistema de procesamiento de facturas con OCR y RPA",
    version="1.0.0",
)

# ── CORS (permite cualquier origen para desarrollo) ──────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registrar routers ────────────────────────────────────────────
app.include_router(auth_router)        # /auth/login, /auth/register, /auth/me
app.include_router(invoice_router)     # /invoices/upload, /trigger-rpa, /rpa-submit, etc.
app.include_router(provider_router)    # /providers CRUD
app.include_router(log_router)         # /logs
app.include_router(dashboard_router)   # /dashboard/metrics, /dashboard/recent

# ── Endpoints básicos ────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "title":   "SmartInvoice — RPA + OCR para facturas",
        "version": "1.0.0",
        "docs":    "/docs",
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/db-test")
async def db_test():
    return {"db_status": test_connection()}