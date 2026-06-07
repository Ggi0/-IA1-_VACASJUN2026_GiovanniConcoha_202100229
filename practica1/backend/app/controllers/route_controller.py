from fastapi import APIRouter, HTTPException

from services.route_service import RouteService
from schemas.route_schema import RouteRequest

router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)

route_service = RouteService()

@router.post("/shortest")
async def get_shortest_route(request: RouteRequest):
    try:
        return route_service.find_shortest_route(
            request.origen,
            request.destino
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/all")
async def get_all_routes(request: RouteRequest):
    try:
        return {
            "rutas": route_service.find_all_routes(
                request.origen,
                request.destino
            )
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )