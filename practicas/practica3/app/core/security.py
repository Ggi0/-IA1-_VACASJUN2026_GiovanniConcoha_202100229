"""
core/security.py
================
Dependencia de FastAPI para extraer y validar el token JWT.
Se usa con Depends() en los controllers.

Uso en cualquier endpoint protegido:
    from app.core.security import get_current_user
    from fastapi import Depends

    @router.get("/algo")
    def mi_endpoint(current_user = Depends(get_current_user), db = Depends(get_db)):
        return {"user": current_user.username}
"""

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.user_repository import UserRepository

SECRET_KEY = os.getenv("SECRET_KEY", "smartinvoice-dev-secret-change-in-prod")
ALGORITHM  = "HS256"

bearer_scheme = HTTPBearer()
user_repo     = UserRepository()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """
    Dependencia que extrae el usuario del token JWT en el header Authorization.
    Úsalo con Depends() en cualquier endpoint protegido.

    Raises:
        HTTPException 401 si el token es inválido, expirado o el usuario no existe.
    """
    token = credentials.credentials

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

    user = user_repo.get_by_id(db, int(user_id))
    if not user or not user.is_active:
        raise credentials_exception

    return user


def require_admin(current_user=Depends(get_current_user)):
    """
    Dependencia adicional que exige rol ADMIN.
    Úsalo en endpoints exclusivos de administrador.

    Raises:
        HTTPException 403 si el usuario no es ADMIN.
    """
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol ADMIN."
        )
    return current_user