"""
AI Code Review Assistant API
Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting AI Code Review Assistant API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Allowed origins: {settings.allowed_origins_list}")

    yield

    # Shutdown
    logger.info("Shutting down AI Code Review Assistant API")


# Create FastAPI application
app = FastAPI(
    title="AI Code Review Assistant API",
    description="Automated code review using AI and static analysis tools",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "AI Code Review Assistant API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    Used by monitoring systems to verify the service is running.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/api/health")
def api_health_check():
    """
    API health check endpoint with more detailed information.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "database": "not_configured",  # Will update in Sprint 1
        "services": {
            "api": "operational",
            "database": "pending",
            "github": "pending",
            "ai": "pending",
        },
    }


# TODO: Include routers in Sprint 1
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(repositories.router, prefix="/api/repositories", tags=["repositories"])
# app.include_router(pull_requests.router, prefix="/api/pulls", tags=["pull_requests"])
# app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
# app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
    )
