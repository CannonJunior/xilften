"""
Main FastAPI application server.

This is the entry point for the XILFTEN API server running on port 7575.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

from config.settings import settings
from config.database import db_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Yields:
        None: Control during application lifetime
    """
    # Startup
    logger.info("=" * 80)
    logger.info(f"🚀 Starting {settings.app_name.upper()} v{settings.app_version}")
    logger.info(f"🌐 Server will run on http://{settings.app_host}:{settings.app_port}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    logger.info("=" * 80)

    # Initialize databases
    try:
        logger.info("📊 Initializing DuckDB...")
        db_manager.get_duckdb_connection()
        logger.info("✅ DuckDB initialized successfully")

        # Run migrations
        logger.info("🔄 Running database migrations...")
        from backend.services.database_service import get_database_service
        db_service = get_database_service()
        db_service.run_migrations()

    except Exception as e:
        logger.error(f"❌ Failed to initialize DuckDB: {e}")

    try:
        logger.info("🧬 Initializing ChromaDB...")
        db_manager.get_chroma_client()
        logger.info("✅ ChromaDB initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize ChromaDB: {e}")

    # Check Ollama availability (if enabled)
    if settings.enable_ai_features:
        logger.info("🤖 Checking Ollama availability...")
        try:
            from backend.services.ollama_client import OllamaClient
            ollama_client = OllamaClient()
            is_healthy = await ollama_client.health_check()

            if is_healthy:
                models = await ollama_client.list_models()
                model_names = [m.get('name') for m in models]
                logger.info(f"✅ Ollama is running with {len(models)} models: {', '.join(model_names)}")
            else:
                logger.warning("⚠️  Ollama server is not responding. AI features may be unavailable.")
        except Exception as e:
            logger.error(f"❌ Ollama health check failed: {str(e)}")

    # Check TMDB API (if enabled)
    if settings.enable_tmdb_sync:
        logger.info("🎬 Checking TMDB API availability...")
        try:
            from backend.services.tmdb_client import tmdb_client
            health_status = await tmdb_client.health_check()

            if health_status["healthy"]:
                logger.info(f"✅ {health_status['message']}")
            elif health_status["status"] == "not_configured":
                logger.warning(f"⚠️  {health_status['message']}")
            else:
                logger.error(f"❌ {health_status['message']}")
        except Exception as e:
            logger.error(f"❌ TMDB health check failed: {str(e)}")

    # Seed default recommendation presets
    logger.info("🎯 Checking recommendation presets...")
    try:
        from backend.services.recommendation_service import recommendation_service
        recommendation_service.seed_default_presets()
        logger.info("✅ Recommendation presets ready")
    except Exception as e:
        logger.error(f"❌ Failed to seed recommendation presets: {str(e)}")

    # Seed genre taxonomy
    logger.info("🎭 Checking genre taxonomy...")
    try:
        from backend.services.genre_service import get_genre_service
        genre_service = get_genre_service()
        result = genre_service.seed_genres()
        logger.info(f"✅ Genres ready: {result['main_genres']} main + {result['subgenres']} sub = {result['total']} total")
    except Exception as e:
        logger.error(f"❌ Failed to seed genres: {str(e)}")

    logger.info("=" * 80)
    logger.info("✨ Application startup complete!")
    logger.info("=" * 80)

    # Yield control during application lifetime
    yield

    # Shutdown
    logger.info("🛑 Shutting down application...")
    db_manager.close_connections()
    logger.info("✅ Shutdown complete")


# Create FastAPI application with lifespan handler
app = FastAPI(
    title=settings.app_name.upper(),
    description="Media multi-use scheduling application with CAG-powered recommendations",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static files for frontend
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    logger.info(f"📁 Mounted static files from: {frontend_dir}")

# Root endpoint - serve frontend
@app.get("/")
async def root():
    """
    Root endpoint - serves frontend HTML.

    Returns:
        FileResponse: Frontend index.html
    """
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    else:
        return {
            "message": f"Welcome to {settings.app_name.upper()} API",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/api/health",
        }


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status of the API and connected services
    """
    health_status = {
        "success": True,
        "data": {
            "status": "healthy",
            "version": settings.app_version,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "services": {
                "database": "unknown",
                "ollama": "unknown",
                "tmdb": "unknown",
            },
        },
    }

    # Check DuckDB
    try:
        conn = db_manager.get_duckdb_connection()
        conn.execute("SELECT 1").fetchone()
        health_status["data"]["services"]["database"] = "connected"
    except Exception as e:
        health_status["data"]["services"]["database"] = f"error: {str(e)}"
        health_status["data"]["status"] = "degraded"

    # Check ChromaDB
    try:
        client = db_manager.get_chroma_client()
        client.heartbeat()
        health_status["data"]["services"]["chromadb"] = "connected"
    except Exception as e:
        health_status["data"]["services"]["chromadb"] = f"error: {str(e)}"
        health_status["data"]["status"] = "degraded"

    # Check TMDB API
    if settings.enable_tmdb_sync:
        try:
            from backend.services.tmdb_client import tmdb_client
            tmdb_health = await tmdb_client.health_check()
            if tmdb_health["healthy"]:
                health_status["data"]["services"]["tmdb"] = "configured"
            elif tmdb_health["status"] == "not_configured":
                health_status["data"]["services"]["tmdb"] = "not_configured"
            else:
                health_status["data"]["services"]["tmdb"] = f"error: {tmdb_health['message']}"
                health_status["data"]["status"] = "degraded"
        except Exception as e:
            health_status["data"]["services"]["tmdb"] = f"error: {str(e)}"
            health_status["data"]["status"] = "degraded"
    else:
        health_status["data"]["services"]["tmdb"] = "disabled"

    # Check Ollama
    if settings.enable_ai_features:
        try:
            from backend.services.ollama_client import OllamaClient
            ollama_client = OllamaClient()
            is_healthy = await ollama_client.health_check()
            if is_healthy:
                health_status["data"]["services"]["ollama"] = "connected"
            else:
                health_status["data"]["services"]["ollama"] = "not_responding"
                health_status["data"]["status"] = "degraded"
        except Exception as e:
            health_status["data"]["services"]["ollama"] = f"error: {str(e)}"
            health_status["data"]["status"] = "degraded"
    else:
        health_status["data"]["services"]["ollama"] = "disabled"

    return health_status


# Version endpoint
@app.get("/api/version")
async def get_version():
    """
    Get API version information.

    Returns:
        dict: Version information
    """
    return {
        "success": True,
        "data": {
            "name": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug,
        },
    }


# Import and include routers
from backend.routes import (
    media_router,
    genres_router,
    recommendations_router,
    calendar_router,
    reviews_router
)
from backend.routes.ai import router as ai_router
from backend.routes.personas import router as personas_router
from backend.routes.bulk_import import router as bulk_import_router

app.include_router(media_router, prefix="/api/media", tags=["Media"])
app.include_router(genres_router, prefix="/api/genres", tags=["Genres"])
app.include_router(recommendations_router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(calendar_router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(reviews_router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(ai_router)  # AI router already has /api/ai prefix
app.include_router(personas_router)  # Personas router already has /api/personas prefix
app.include_router(bulk_import_router)  # Bulk import router already has /api/bulk prefix


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.server:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=False,  # Disabled auto-reload
        log_level=settings.log_level.lower(),
    )
