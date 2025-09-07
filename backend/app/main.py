"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import time
import uuid
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine
from app.core.logging import setup_logging
from app.api.api_v1.api import api_router
from app.core.security import get_current_user
from app.core.exceptions import (
    NotebookLMException,
    ValidationException,
    AuthenticationException,
    PermissionException,
)

# Setup structured logging
setup_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting NotebookLM RAG System", version=settings.VERSION)
    
    # Initialize database connection
    try:
        # Test database connection
        from app.core.database import get_db
        next(get_db())
        logger.info("Database connection established")
    except Exception as e:
        logger.error("Failed to connect to database", error=str(e))
        raise
    
    # Initialize Redis connection
    try:
        from app.core.cache import redis_client
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error("Failed to connect to Redis", error=str(e))
        # Redis is not critical, continue without it
    
    yield
    
    # Shutdown
    logger.info("Shutting down NotebookLM RAG System")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-ready RAG system using Google's NotebookLM API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.ALLOWED_HOSTS
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time and correlation ID to headers."""
    # Generate correlation ID for request tracing
    correlation_id = str(uuid.uuid4())
    
    # Add correlation ID to request state
    request.state.correlation_id = correlation_id
    
    # Log request start
    start_time = time.time()
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        correlation_id=correlation_id,
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Add headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Correlation-ID"] = correlation_id
    
    # Log request completion
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time,
        correlation_id=correlation_id,
    )
    
    return response


# Exception handlers
@app.exception_handler(NotebookLMException)
async def notebooklm_exception_handler(request: Request, exc: NotebookLMException):
    """Handle NotebookLM API exceptions."""
    logger.error(
        "NotebookLM API error",
        error=str(exc),
        correlation_id=getattr(request.state, "correlation_id", None),
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error with NotebookLM API",
            "error_type": "notebooklm_error",
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle validation exceptions."""
    logger.warning(
        "Validation error",
        error=str(exc),
        correlation_id=getattr(request.state, "correlation_id", None),
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": str(exc),
            "error_type": "validation_error",
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )


@app.exception_handler(AuthenticationException)
async def authentication_exception_handler(request: Request, exc: AuthenticationException):
    """Handle authentication exceptions."""
    logger.warning(
        "Authentication error",
        error=str(exc),
        correlation_id=getattr(request.state, "correlation_id", None),
    )
    return JSONResponse(
        status_code=401,
        content={
            "detail": "Authentication failed",
            "error_type": "authentication_error",
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )


@app.exception_handler(PermissionException)
async def permission_exception_handler(request: Request, exc: PermissionException):
    """Handle permission exceptions."""
    logger.warning(
        "Permission error",
        error=str(exc),
        correlation_id=getattr(request.state, "correlation_id", None),
    )
    return JSONResponse(
        status_code=403,
        content={
            "detail": "Permission denied",
            "error_type": "permission_error",
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time(),
    }


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "NotebookLM RAG System API",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
