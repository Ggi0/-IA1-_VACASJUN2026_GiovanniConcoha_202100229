from pydantic import BaseModel
from typing import List, Optional


class PreguntaCreateRequest(BaseModel):
    pregunta: str
    respuesta: str
    categoria_id: int
    palabras_clave: List[str]


class PreguntaUpdateRequest(BaseModel):
    pregunta: str
    respuesta: str
    categoria_id: int
    palabras_clave: List[str]


class PalabraClaveResponse(BaseModel):
    id: int
    palabra: str

    class Config:
        orm_mode = True


class CategoriaResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        orm_mode = True


class PreguntaResponse(BaseModel):
    id: int
    pregunta: str
    respuesta: str
    activa: bool

    categoria: CategoriaResponse
    palabras_clave: List[PalabraClaveResponse]

    class Config:
        orm_mode = True