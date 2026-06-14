import os

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.repositories.usuario_repository import UsuarioRepository


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-this")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES", "120")
)


class AuthService:

    @staticmethod
    def verificar_password(
        password_plano: str,
        password_hash: str
    ) -> bool:
        return pwd_context.verify(password_plano, password_hash)

    @staticmethod
    def generar_hash_password(password_plano: str) -> str:
        hashed = pwd_context.hash("admin123")
        print(hashed) 
        return pwd_context.hash(password_plano)

    @staticmethod
    def crear_access_token(data: dict):
        to_encode = data.copy()

        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

        to_encode.update({"exp": expire})

        return jwt.encode(
            to_encode,
            SECRET_KEY,
            algorithm=ALGORITHM
        )

    @staticmethod
    def login(
        db: Session,
        usuario: str,
        password: str
    ):
        user = UsuarioRepository.obtener_por_usuario(
            db,
            usuario
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )

        if not user.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario está inactivo"
            )

        if user.rol.lower() not in ["admin", "administrador"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario no tiene permisos de administrador"
            )

        if not AuthService.verificar_password(
            password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )

        token = AuthService.crear_access_token(
            {
                "sub": str(user.id),
                "usuario": user.usuario,
                "rol": user.rol
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "usuario": {
                "id": user.id,
                "nombre": user.nombre,
                "usuario": user.usuario,
                "correo": user.correo,
                "rol": user.rol
            }
        }