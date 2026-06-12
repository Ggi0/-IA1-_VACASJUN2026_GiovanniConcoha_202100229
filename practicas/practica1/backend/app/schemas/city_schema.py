from pydantic import BaseModel

class CityRequest(BaseModel):
    nombre: str

class ConnectionRequest(BaseModel):
    origen: str
    destino: str
    distancia: int