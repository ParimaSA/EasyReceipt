from fastapi import APIRouter
from app.api.v1.endpoints import auth, records, groups, categories

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(records.router)
api_router.include_router(groups.router)
api_router.include_router(categories.router)
