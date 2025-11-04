"""
Main FastAPI application server.

This is the entry point for the XILFTEN API server running on port 7575.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import sys

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

# Create FastAPI application
app = FastAPI(
    title=settings.app_name.upper(),
    description="Media multi-use scheduling application with CAG-powered recommendations",
    version=settings.app_version,
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup.

    Initializes database connections and performs health checks.
    """
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
        # TODO: Implement Ollama health check
        logger.info("⚠️  Ollama health check not yet implemented")

    # Check TMDB API (if enabled)
    if settings.enable_tmdb_sync:
        logger.info("🎬 Checking TMDB API availability...")
        if not settings.tmdb_api_key or settings.tmdb_api_key == "":
            logger.warning("⚠️  TMDB API key not configured")
        else:
            # TODO: Implement TMDB health check
            logger.info("⚠️  TMDB health check not yet implemented")

    logger.info("=" * 80)
    logger.info("✨ Application startup complete!")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown.

    Closes database connections and performs cleanup.
    """
    logger.info("🛑 Shutting down application...")
    db_manager.close_connections()
    logger.info("✅ Shutdown complete")


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint.

    Returns:
        dict: Welcome message and API information
    """
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

    # TODO: Add Ollama and TMDB health checks

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


# TODO: Import and include routers
# from backend.routes import media, genres, reviews, calendar, recommendations, ai, criteria

# app.include_router(media.router, prefix="/api/media", tags=["Media"])
# app.include_router(genres.router, prefix="/api/genres", tags=["Genres"])
# app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
# app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
# app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
# app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
# app.include_router(criteria.router, prefix="/api/criteria", tags=["Criteria"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.server:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
