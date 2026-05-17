"""
SupBuddy Logistics Tracking System - FastAPI Main Application

This is the main entry point for the FastAPI application. It configures:
- Application lifecycle (startup/shutdown)
- Database initialization
- Background scheduler for SLA monitoring
- CORS middleware for frontend integration
- API routing structure
- Health check endpoints
- Global exception handlers
- Structured logging

Usage:
    Development:
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
    
    Production:
        uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    
    With custom settings:
        LOG_LEVEL=DEBUG uvicorn main:app --reload

API Documentation:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - OpenAPI JSON: http://localhost:8000/openapi.json
"""
from contextlib import asynccontextmanager
from typing import Dict, Any
import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.core.database import init_db, close_db
from app.core.scheduler import scheduler_manager
from app.core.logging_config import setup_logging

# Initialize logging first
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    Startup:
        1. Initialize database tables
        2. Start APScheduler for background jobs
        3. Log application startup
    
    Shutdown:
        1. Stop scheduler gracefully
        2. Close database connections
        3. Log application shutdown
    """
    # Startup
    logger.info("=" * 80)
    logger.info("Starting SupBuddy Logistics Tracking System")
    logger.info("=" * 80)
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        
        # Start scheduler
        logger.info("Starting background scheduler...")
        scheduler_manager.start()
        logger.info("Background scheduler started successfully")
        
        logger.info("Application startup complete")
        logger.info(f"API documentation available at: http://localhost:8000/docs")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("=" * 80)
    logger.info("Shutting down SupBuddy Logistics Tracking System")
    logger.info("=" * 80)
    
    try:
        # Stop scheduler
        logger.info("Stopping background scheduler...")
        scheduler_manager.shutdown()
        logger.info("Background scheduler stopped")
        
        # Close database
        logger.info("Closing database connections...")
        await close_db()
        logger.info("Database connections closed")
        
        logger.info("Application shutdown complete")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"CORS configured with origins: {settings.cors_origins}")


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with detailed error messages.
    
    Returns:
        422 Unprocessable Entity with validation error details
    """
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database errors gracefully.
    
    Returns:
        500 Internal Server Error with generic message (hides DB details)
    """
    logger.error(f"Database error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database Error",
            "detail": "An error occurred while processing your request. Please try again later.",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all other unhandled exceptions.
    
    Returns:
        500 Internal Server Error with generic message
    """
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
        },
    )


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.
    
    Returns:
        Simple status message indicating the service is running
        
    Example:
        GET /health
        Response: {"status": "healthy"}
    """
    return {"status": "healthy"}


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with component status.
    
    Returns:
        Detailed status of all application components:
        - Overall status
        - Database connection status
        - Scheduler status and active jobs
        - Application version
        
    Example:
        GET /health/detailed
        Response: {
            "status": "healthy",
            "version": "1.0.0",
            "components": {
                "database": "connected",
                "scheduler": {
                    "status": "running",
                    "jobs": [...]
                }
            }
        }
    """
    # Get scheduler status
    scheduler_status = scheduler_manager.get_job_status()
    
    # Build detailed health response
    health_data = {
        "status": "healthy",
        "version": settings.api_version,
        "components": {
            "database": "connected",  # If we got here, DB is working
            "scheduler": scheduler_status,
        },
        "configuration": {
            "log_level": settings.log_level,
            "scheduler_enabled": settings.scheduler_enabled,
            "sla_eval_interval_minutes": settings.sla_eval_interval_minutes,
            "tracking_pull_interval_minutes": settings.tracking_pull_interval_minutes,
        },
    }
    
    return health_data


# ============================================================================
# API Router Structure
# ============================================================================

# Import API v1 router
from app.api.v1 import router as api_v1_router

# Include API v1 router with prefix
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)
logger.info(f"API v1 routes registered at {settings.api_v1_prefix}")


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint with API information.
    
    Returns:
        API metadata and available endpoints
    """
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
        "health": {
            "basic": "/health",
            "detailed": "/health/detailed",
        },
        "api": {
            "v1": {
                "base": settings.api_v1_prefix,
                "endpoints": {
                    "shipments": f"{settings.api_v1_prefix}/shipments",
                    "schedules": f"{settings.api_v1_prefix}/schedules",
                    "alerts": f"{settings.api_v1_prefix}/alerts",
                }
            }
        },
    }


# ============================================================================
# Application Metadata
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # This allows running the app directly with: python main.py
    # For production, use: uvicorn main:app
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower(),
    )

# Made with Bob