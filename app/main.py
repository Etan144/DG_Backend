from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.health import router as health_router
from app.api.calls import router as call_router
from app.api.firebase_api import router as firebase_router

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(title=settings.app_name)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Dynamic CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://fyp-25-s4-23-1.onrender.com,http://localhost:3000,http://localhost:5173,http://localhost:5500,http://127.0.0.1:5500").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

logger.info(f"Allowed CORS origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Global exception handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error for {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        },
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    logger.warning(f"Rate limit exceeded for {request.client.host} on {request.url.path}")
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("DG Backend API starting up...")
    logger.info(f"Environment: {settings.env}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("DG Backend API shutting down...")

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(call_router)
app.include_router(firebase_router)

logger.info("DG Backend API initialized successfully")
