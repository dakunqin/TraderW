from fastapi import APIRouter

from app.api.routes import api_keys, auth, debug, mt5_ea, mt5_web

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(mt5_ea.router, prefix="/mt5", tags=["mt5-ea"])
api_router.include_router(mt5_web.router, tags=["mt5-web"])
api_router.include_router(debug.router, tags=["debug"])
