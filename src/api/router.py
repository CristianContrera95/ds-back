from fastapi import APIRouter
from api.views import (
    model_view, login
)

api_router = APIRouter()
api_router.include_router(login.router, prefix="/auth")
api_router.include_router(model_view.router, prefix="/models")


@api_router.get("/")
async def hello():
    return {"server": "API ML Platform"}
