import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI) -> None:
    """Registers standard, uniform exception interceptors on the FastAPI instance."""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTPException [{exc.status_code}]: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        logger.warning(f"ValueError caught: {exc}")
        # Convert Pydantic / Validation exceptions to standard 400 Bad Request securely
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError):
        logger.error(f"PermissionError boundary violation: {exc}")
        # Enforce fail-closed secure boundaries
        return JSONResponse(
            status_code=403,
            content={"detail": "Access denied due to boundary restrictions."}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # 1. Secure Server-Side Logging
        logger.critical(f"Unhandled system crash: {str(exc)}", exc_info=True)
        
        # 2. Generic safe client response (No stack traces or sensitive leaks)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected internal server error occurred."}
        )
