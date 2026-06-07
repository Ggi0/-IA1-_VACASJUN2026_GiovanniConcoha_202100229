from pydantic import BaseModel

class RouteRequest(BaseModel):
    origen: str
    destino: str