from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import test_connection

app = FastAPI(
    title="Proyecto 3 - SmartInvoice",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "title": "RPA-OCR para facturas",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

#endpoint de prueba DB
@app.get("/db-test")
async def db_test():
    return {
        "db_status": test_connection()
    }
