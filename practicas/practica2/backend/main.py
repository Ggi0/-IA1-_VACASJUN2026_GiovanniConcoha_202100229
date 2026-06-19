from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from app.config.db import verificar_conexion



from app.routes import auth_routes
from app.routes import admin_pregunta_routes
from app.routes import admin_telegram_chat_routes

from app.service.bot_polling_service import BotPollingService


app = FastAPI(
    title="Practica 2 - Backend, smartbot",
)

@app.on_event("startup")
async def startup():

    verificar_conexion()
    BotPollingService.iniciar()

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




app.include_router(auth_routes.router)
app.include_router(admin_pregunta_routes.router)
app.include_router(admin_telegram_chat_routes.router)
