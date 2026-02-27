from fastapi import APIRouter

from social.api.v1 import accounts, entities, health, posts

api_router = APIRouter()
api_router.include_router(health.router, prefix="/api/v1")
api_router.include_router(entities.router, prefix="/api/v1")
api_router.include_router(accounts.router, prefix="/api/v1")
api_router.include_router(posts.router, prefix="/api/v1")
