from pydantic import BaseModel


class LoginRequest(BaseModel):
    usuario: str
    password: str


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    usuario: str
    correo: str
    rol: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioResponse