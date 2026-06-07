from fastapi import FastAPI

from controllers.route_controller import router as route_router
from controllers.city_controller import router as city_router

app = FastAPI(
    title="Transport Routing System"
)

app.include_router(route_router)
app.include_router(city_router)