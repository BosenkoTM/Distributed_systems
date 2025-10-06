from fastapi import APIRouter
from app.api.v1.endpoints import sessions, labeling, files, monitoring

api_router = APIRouter()

# Подключение всех endpoints
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(labeling.router, prefix="/labeling", tags=["labeling"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
