import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.middleware.security import SecurityHeadersMiddleware, SafeLoggingMiddleware

# Logger setup
logger = logging.getLogger(__name__)

# Rate Limiter setup
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing GitHub RAG Documentation System Backend...")
    # Ensure temporary and generated docs directories exist safely
    import os
    os.makedirs(settings.SANDBOX_DIR, exist_ok=True)
    os.makedirs(settings.GENERATED_DOCS_DIR, exist_ok=True)
    
    yield
    
    # Shutdown actions
    logger.info("Shutting down GitHub RAG Documentation System Backend...")

# Create FastAPI app
app = FastAPI(
    title="GitHub RAG Documentation System",
    description="Backend API for semantically analyzing and documenting GitHub repositories using RAG.",
    version="1.0.0",
    lifespan=lifespan
)

# Set rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register secure global exception handlers
from app.utils.error_handler import register_exception_handlers
register_exception_handlers(app)

# 1. Add Safe Logging Middleware (Outer layer)
app.add_middleware(SafeLoggingMiddleware)

# 2. Add Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 3. Add CORS Middleware (Strict allowlist, no wildcards)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

from app.api.routes import health, analyze, jobs

# Root endpoint for health check / status
@app.get("/")
@limiter.limit("30/minute")
async def root():
    return {"status": "running", "service": "GitHub Repository RAG Documentation System"}

# Register Router endpoints
app.include_router(health.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
