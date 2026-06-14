from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from app.config.db import verificar_conexion


app = FastAPI(
    title="Practica 2 - Backend, smartbot",
)

@app.on_event("startup")
async def startup():

    verificar_conexion()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # URL de tu frontend con Vite
    allow_credentials=True,
    allow_methods=["*"],   # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],   # Permite todos los headers
)

@app.get("/")
async def health():
    return {
        "title": "smart-bot",
        "description": "Sistema de respuestas automatizadas, basado en un bot de telegram",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "ok - practica2"}


