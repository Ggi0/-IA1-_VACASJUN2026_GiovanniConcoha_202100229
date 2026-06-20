"""
provider_controller.py
======================
CRUD completo de proveedores.

Endpoints:
    GET    /providers        → Lista todos
    GET    /providers/{id}   → Detalle por ID
    POST   /providers        → Crear (ADMIN)
    PUT    /providers/{id}   → Actualizar (ADMIN)
    DELETE /providers/{id}   → Eliminar (ADMIN)
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_admin
from app.services.provider_service import ProviderService

router = APIRouter(prefix="/providers", tags=["Providers"])
provider_service = ProviderService()


# ─────────────────────────────────────────────────────────────────
# GET /providers — Lista todos los proveedores
# Cualquier usuario autenticado puede verlos.
# ─────────────────────────────────────────────────────────────────
@router.get("/")
def get_providers(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Respuesta 200: lista de proveedores con id, name, nit, address, phone, created_at.
    """
    return provider_service.get_all(db)


# ─────────────────────────────────────────────────────────────────
# GET /providers/{id} — Detalle de un proveedor
# ─────────────────────────────────────────────────────────────────
@router.get("/{provider_id}")
def get_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Path param: provider_id (int)
    Error 404 si no existe.
    """
    return provider_service.get_by_id(db, provider_id)


# ─────────────────────────────────────────────────────────────────
# POST /providers — Crear proveedor (solo ADMIN)
# ─────────────────────────────────────────────────────────────────
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_provider(
    body: dict,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """
    Body:
        {
            "name": "Papelería Central S.A.",
            "nit": "7654321-0",
            "address": "3a Calle 5-12, Zona 4",   ← opcional
            "phone": "55556666"                     ← opcional
        }

    Respuesta 201: objeto proveedor creado con su ID asignado.
    Error 409: NIT ya existe.
    Error 422: NIT con formato inválido o nombre vacío.
    """
    return provider_service.create(db, body)


# ─────────────────────────────────────────────────────────────────
# PUT /providers/{id} — Actualizar proveedor (solo ADMIN)
# ─────────────────────────────────────────────────────────────────
@router.put("/{provider_id}")
def update_provider(
    provider_id: int,
    body: dict,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """
    Body (solo los campos que quieres cambiar):
        {
            "name": "Nuevo nombre",
            "phone": "44447777"
        }

    Respuesta 200: objeto proveedor actualizado.
    Error 404: proveedor no encontrado.
    Error 409: el NIT nuevo ya pertenece a otro proveedor.
    """
    return provider_service.update(db, provider_id, body)


# ─────────────────────────────────────────────────────────────────
# DELETE /providers/{id} — Eliminar proveedor (solo ADMIN)
# Falla con 409 si el proveedor tiene facturas asociadas.
# ─────────────────────────────────────────────────────────────────
@router.delete("/{provider_id}")
def delete_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """
    Respuesta 200: { "message": "Proveedor ID 6 eliminado correctamente." }
    Error 404: proveedor no encontrado.
    Error 409: tiene facturas asociadas, no se puede eliminar.
    """
    return provider_service.delete(db, provider_id)