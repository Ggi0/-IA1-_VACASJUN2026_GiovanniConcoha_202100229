"""
provider_service.py
===================
CRUD completo de proveedores.
La validación del NIT reutiliza ValidationService para no duplicar lógica.

Consume: ProviderRepository
Es consumido por: provider_controller.py
"""

import logging
import re
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.provider_repository import ProviderRepository

logger = logging.getLogger(__name__)

NIT_REGEX = re.compile(r"^\d{6,8}-[0-9K]$", re.IGNORECASE)
NIT_CF_REGEX = re.compile(r"^C\.?F\.?$", re.IGNORECASE)


class ProviderService:

    def __init__(self):
        self.repo = ProviderRepository()

    def get_all(self, db: Session) -> list:
        """Retorna lista de todos los proveedores."""
        providers = self.repo.get_all(db)
        return [self._serialize(p) for p in providers]

    def get_by_id(self, db: Session, provider_id: int) -> dict:
        """Retorna un proveedor por ID."""
        provider = self.repo.get_by_id(db, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Proveedor ID {provider_id} no encontrado.")
        return self._serialize(provider)

    def create(self, db: Session, data: dict) -> dict:
        """
        Crea un nuevo proveedor.
        Valida que el NIT sea único y con formato correcto.
        """
        nit = str(data.get("nit", "")).strip().upper()

        # Validar formato NIT
        if not (NIT_REGEX.match(nit) or NIT_CF_REGEX.match(nit)):
            raise HTTPException(
                status_code=422,
                detail=f"NIT '{nit}' no tiene formato válido. Use: 1234567-8 o CF."
            )

        # Verificar unicidad
        existing = self.repo.get_by_nit(db, nit)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un proveedor con NIT '{nit}' (ID={existing.id})."
            )

        name = str(data.get("name", "")).strip()
        if len(name) < 2:
            raise HTTPException(status_code=422, detail="Nombre del proveedor requerido (mínimo 2 caracteres).")

        provider = self.repo.create(db, {
            "name":    name,
            "nit":     nit,
            "address": data.get("address"),
            "phone":   data.get("phone"),
        })

        logger.info(f"Proveedor creado: {name} (NIT={nit})")
        return self._serialize(provider)

    def update(self, db: Session, provider_id: int, data: dict) -> dict:
        """
        Actualiza un proveedor existente.
        Si se cambia el NIT, verifica que no esté en uso por otro proveedor.
        """
        provider = self.repo.get_by_id(db, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Proveedor ID {provider_id} no encontrado.")

        if "nit" in data:
            new_nit = str(data["nit"]).strip().upper()
            if not (NIT_REGEX.match(new_nit) or NIT_CF_REGEX.match(new_nit)):
                raise HTTPException(status_code=422, detail=f"NIT '{new_nit}' no tiene formato válido.")

            existing = self.repo.get_by_nit(db, new_nit)
            if existing and existing.id != provider_id:
                raise HTTPException(
                    status_code=409,
                    detail=f"El NIT '{new_nit}' ya pertenece al proveedor ID={existing.id}."
                )
            data["nit"] = new_nit

        updated = self.repo.update(db, provider, data)
        logger.info(f"Proveedor actualizado ID={provider_id}")
        return self._serialize(updated)

    def delete(self, db: Session, provider_id: int) -> dict:
        """
        Elimina un proveedor.
        Si tiene facturas asociadas, lanza 409 para no romper integridad referencial.
        """
        provider = self.repo.get_by_id(db, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Proveedor ID {provider_id} no encontrado.")

        # Verificar facturas asociadas
        if provider.invoices:
            raise HTTPException(
                status_code=409,
                detail=f"No se puede eliminar: el proveedor tiene {len(provider.invoices)} factura(s) asociada(s)."
            )

        self.repo.delete(db, provider)
        logger.info(f"Proveedor eliminado ID={provider_id}")
        return {"message": f"Proveedor ID {provider_id} eliminado correctamente."}

    @staticmethod
    def _serialize(provider) -> dict:
        return {
            "id":         provider.id,
            "name":       provider.name,
            "nit":        provider.nit,
            "address":    provider.address,
            "phone":      provider.phone,
            "created_at": str(provider.created_at) if provider.created_at else None,
        }