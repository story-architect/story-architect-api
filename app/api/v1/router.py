from fastapi import APIRouter

from app.api.v1 import auth, characters, discovery, relationships, reports, stories

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(stories.router, prefix="/stories", tags=["stories"])
api_router.include_router(
    characters.router, tags=["characters"]
)  # Note: The prompt asks for nested routes like /stories/{story_id}/characters, which we will handle inside characters.router
api_router.include_router(relationships.router, tags=["relationships"])
api_router.include_router(discovery.router, prefix="/discovery", tags=["discovery"])
api_router.include_router(reports.router, tags=["reports"])
