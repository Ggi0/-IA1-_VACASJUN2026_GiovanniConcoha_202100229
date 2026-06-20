"""
auth_controller.py
==================
Endpoints de autenticación.

Endpoints:
    POST /auth/login     → Recibe credenciales, retorna token JWT
    POST /auth/register  → Crea nuevo usuario (solo ADMIN)
    GET  /auth/me        → Retorna datos del usuario autenticado
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()


# ─────────────────────────────────────────────────────────────────
# POST /auth/login
# No requiere token. El empleado o admin envía sus credenciales.
# Retorna el JWT que el frontend guarda en localStorage.
# ─────────────────────────────────────────────────────────────────
@router.post("/login")
def login(body: dict, db: Session = Depends(get_db)):
    """
    Body esperado:
        { "username": "admin", "password": "mi_password" }

    Respuesta 200:
        { "access_token": "eyJ...", "token_type": "bearer", "user": { ... } }
    """
    return auth_service.login(
        db=db,
        username=body.get("username", ""),
        password=body.get("password", ""),
    )


# ─────────────────────────────────────────────────────────────────
# POST /auth/register
# Solo ADMIN puede crear usuarios. Protegido con require_admin.
# ─────────────────────────────────────────────────────────────────
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    body: dict,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),          # Lanza 403 si no es ADMIN
):
    """
    Body esperado:
        {
            "username": "empleado2",
            "email": "emp2@empresa.com",
            "password": "password123",
            "role": "EMPLOYEE"             ← opcional, default EMPLOYEE
        }

    Respuesta 201:
        { "id": 3, "username": "empleado2", "email": "...", "role": "EMPLOYEE" }
    """
    return auth_service.register(
        db=db,
        username=body.get("username", ""),
        email=body.get("email", ""),
        password=body.get("password", ""),
        role=body.get("role", "EMPLOYEE"),
    )


# ─────────────────────────────────────────────────────────────────
# GET /auth/me
# Devuelve los datos del usuario dueño del token actual.
# ─────────────────────────────────────────────────────────────────
@router.get("/me")
def me(current_user=Depends(get_current_user)):
    """
    Requiere: Authorization: Bearer <token>

    Respuesta 200:
        { "id": 1, "username": "admin", "email": "...", "role": "ADMIN", "is_active": true }
    """
    return {
        "id":        current_user.id,
        "username":  current_user.username,
        "email":     current_user.email,
        "role":      current_user.role.value,
        "is_active": current_user.is_active,
    }