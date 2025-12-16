# -*- coding: utf-8 -*-
"""
Main application entry point

This module sets up the FastAPI application with:
- UTF-8 encoding enforcement
- CORS middleware
- API routers
- Error handling
"""
import sys
import os

# Ensure UTF-8 encoding
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from config import APP_NAME, APP_VERSION, CORS_ORIGINS, DEBUG
from models.response import ApiResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO if DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="A pixel art themed toolbox for image, PDF, and text processing",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# UTF-8 charset middleware
@app.middleware("http")
async def add_utf8_charset(request: Request, call_next):
    """Ensure all JSON responses include UTF-8 charset"""
    response = await call_next(request)
    if "application/json" in response.headers.get("content-type", ""):
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response time
    process_time = time.time() - start_time
    logger.info(f"Completed in {process_time:.3f}s - Status: {response.status_code}")

    return response


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return ApiResponse.success(
        data={
            "name": APP_NAME,
            "version": APP_VERSION,
            "status": "running",
            "docs": "/docs" if DEBUG else "disabled in production"
        },
        message="API is running"
    )


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return ApiResponse.success(
        data={
            "status": "healthy",
            "version": APP_VERSION,
        },
        message="Service is healthy"
    )


# Include routers
from routers import image, text, pdf, ai, youtube, settings, audio

app.include_router(image.router, prefix="/api/image", tags=["Image Tools"])
app.include_router(text.router, prefix="/api/text", tags=["Text Tools"])
app.include_router(pdf.router, prefix="/api/pdf", tags=["PDF Tools"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Tools"])
app.include_router(youtube.router, prefix="/api/youtube", tags=["YouTube Tools"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(audio.router, prefix="/api/audio", tags=["Audio Tools"])


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"CORS origins: {CORS_ORIGINS}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info(f"Shutting down {APP_NAME}")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ApiResponse.server_error(
            message=str(exc) if DEBUG else "Internal server error"
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if DEBUG else "warning"
    )
