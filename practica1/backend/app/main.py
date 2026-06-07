from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from adapters.prolog_adapter import PrologAdapter

app = FastAPI()

# Instancia del adaptador para comunicarse con Prolog
prolog_adapter = PrologAdapter()

# Modelos para las solicitudes
class RouteRequest(BaseModel):
    origen: str
    destino: str

class CityRequest(BaseModel):
    nombre: str

class ConnectionRequest(BaseModel):
    origen: str
    destino: str
    distancia: int

# Endpoint para buscar la ruta más corta
@app.post("/routes/shortest")
async def get_shortest_route(request: RouteRequest):
    try:
        result = prolog_adapter.find_shortest_route(request.origen, request.destino)
        return {"ruta": result["ruta"], "distancia": result["distancia"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para obtener todas las rutas entre dos ciudades
@app.post("/routes/all")
async def get_all_routes(request: RouteRequest):
    try:
        result = prolog_adapter.find_all_routes(request.origen, request.destino)
        return {"rutas": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para obtener todas las ciudades
@app.get("/cities")
async def get_cities():
    try:
        cities = prolog_adapter.get_all_cities()
        return {"ciudades": cities}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para agregar una nueva ciudad
@app.post("/cities")
async def add_city(request: CityRequest):
    try:
        prolog_adapter.add_city(request.nombre)
        return {"message": f"Ciudad '{request.nombre}' agregada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para agregar una nueva conexión
@app.post("/connections")
async def add_connection(request: ConnectionRequest):
    try:
        prolog_adapter.add_connection(request.origen, request.destino, request.distancia)
        return {"message": f"Conexión entre '{request.origen}' y '{request.destino}' agregada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))