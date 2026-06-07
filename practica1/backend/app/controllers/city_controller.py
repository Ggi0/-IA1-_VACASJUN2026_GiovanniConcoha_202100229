from fastapi import APIRouter, HTTPException

from services.city_service import CityService
from schemas.city_schema import (
    CityRequest,
    ConnectionRequest
)

router = APIRouter(
    tags=["Cities"]
)

city_service = CityService()

@router.get("/cities")
async def get_cities():
    try:
        return {
            "ciudades": city_service.get_all_cities()
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/cities")
async def add_city(request: CityRequest):
    try:

        city_service.add_city(
            request.nombre
        )

        return {
            "message":
            f"Ciudad '{request.nombre}' agregada exitosamente"
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/connections")
async def add_connection(
    request: ConnectionRequest
):
    try:

        city_service.add_connection(
            request.origen,
            request.destino,
            request.distancia
        )

        return {
            "message":
            "Conexión agregada exitosamente"
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/connections")
async def get_connections():

    try:

        return {
            "connections":
            city_service.get_all_connections()
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )