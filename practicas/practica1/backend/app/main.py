from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware


from controllers.route_controller import router as route_router
from controllers.city_controller import router as city_router

app = FastAPI(
    title="Transport Routing System"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],  # URL de tu frontend con Vite
    allow_credentials=True,
    allow_methods=["*"],   # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],   # Permite todos los headers
)

app.include_router(route_router)
app.include_router(city_router)