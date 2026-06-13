from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware


from app.controllers.usuarios import router as usuarios_router
from app.controllers.admin import router as admin_router
# from controllers.city_controller import router as city_router

app = FastAPI(
    title="Proyecto 1 - Backend",
)

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
        "title": "Diagnosticador de Pc",
        "description": "API para diagnosticar problemas comunes en computadoras utilizando un motor de inferencia basado en Prolog.",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(usuarios_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

#app.include_router(route_router)
#app.include_router(city_router)


