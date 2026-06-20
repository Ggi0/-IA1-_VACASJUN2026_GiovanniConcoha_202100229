"""
auth_service.py
===============
Servicio de autenticación.
Maneja login, creación de tokens JWT y registro de usuarios.

Consume: UserRepository
Es consumido por: auth_controller.py
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

# ── Configuración JWT ────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "smartinvoice-dev-secret-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))  # 8 horas

# ── Hashing de contraseñas ───────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    def __init__(self):
        self.user_repo = UserRepository()

    # ─────────────────────────────────────────────────────────────
    # LOGIN
    # ─────────────────────────────────────────────────────────────

    def login(self, db: Session, username: str, password: str) -> dict:
        """
        Verifica credenciales y retorna el token JWT.

        Args:
            db:       Sesión de base de datos.
            username: Nombre de usuario.
            password: Contraseña en texto plano.

        Returns:
            dict con access_token, token_type y datos básicos del usuario.

        Raises:
            HTTPException 401 si las credenciales son inválidas.
        """
        user = self.user_repo.get_by_username(db, username)

        if not user or not self._verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo. Contacta al administrador.",
            )

        token = self._create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value}
        )

        logger.info(f"Login exitoso: {username} (ID={user.id}, role={user.role.value})")

        return {
            "access_token": token,
            "token_type":   "bearer",
            "user": {
                "id":       user.id,
                "username": user.username,
                "email":    user.email,
                "role":     user.role.value,
            }
        }

    # ─────────────────────────────────────────────────────────────
    # REGISTRO
    # ─────────────────────────────────────────────────────────────

    def register(self, db: Session, username: str, email: str, password: str, role: str = "EMPLOYEE") -> dict:
        """
        Crea un nuevo usuario. Solo ADMIN puede crear otros ADMIN.

        Args:
            db:       Sesión de base de datos.
            username: Nombre de usuario único.
            email:    Email único.
            password: Contraseña en texto plano (se hashea aquí).
            role:     "ADMIN" | "EMPLOYEE" (default: EMPLOYEE).

        Returns:
            dict con los datos del usuario creado (sin password).

        Raises:
            HTTPException 409 si el username o email ya existe.
        """
        # Verificar que no exista el username
        if self.user_repo.get_by_username(db, username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El usuario '{username}' ya existe.",
            )

        hashed = self._hash_password(password)

        user = self.user_repo.create_user(db, {
            "username": username,
            "email":    email,
            "password": hashed,
            "role":     role,
        })

        logger.info(f"Usuario creado: {username} (role={role})")

        return {
            "id":       user.id,
            "username": user.username,
            "email":    user.email,
            "role":     user.role.value,
        }

    # ─────────────────────────────────────────────────────────────
    # OBTENER USUARIO ACTUAL (para Depends en FastAPI)
    # ─────────────────────────────────────────────────────────────

    def get_current_user(self, db: Session, token: str):
        """
        Decodifica el token JWT y retorna el usuario correspondiente.
        Úsalo como dependencia en los controllers:

            from app.core.security import get_current_user
            current_user = Depends(get_current_user)

        Args:
            db:    Sesión de base de datos.
            token: Token JWT extraído del header Authorization.

        Returns:
            Objeto User del ORM.

        Raises:
            HTTPException 401 si el token es inválido o el usuario no existe.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = self.user_repo.get_by_id(db, int(user_id))
        if not user:
            raise credentials_exception

        return user

    # ─────────────────────────────────────────────────────────────
    # Helpers privados
    # ─────────────────────────────────────────────────────────────

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)