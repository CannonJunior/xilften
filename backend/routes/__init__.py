"""API routes package."""

from .media import router as media_router
from .genres import router as genres_router
from .recommendations import router as recommendations_router
from .calendar import router as calendar_router
from .reviews import router as reviews_router

__all__ = [
    "media_router",
    "genres_router",
    "recommendations_router",
    "calendar_router",
    "reviews_router"
]
