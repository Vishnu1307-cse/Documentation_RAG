import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# Allowed HTTP methods allow-list
ALLOWED_METHODS = {"GET", "POST"}

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Check HTTP method
        if request.method not in ALLOWED_METHODS:
            logger.warning(f"Blocked request with disallowed method: {request.method}")
            return JSONResponse(
                status_code=405,
                content={"detail": f"Method {request.method} is not allowed."}
            )

        # Call down the middleware chain
        response = await call_next(request)

        # Inject security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Permissions policy - disable hardware features
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), usb=(), payment=()"
        )
        
        # CSP frame-ancestors self to prevent clickjacking
        response.headers["Content-Security-Policy"] = "frame-ancestors 'none';"
        
        return response

class SafeLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Secure logging: Log incoming requests without logging request bodies or sensitive query params
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"Incoming Request: {request.method} {request.url.path} from {client_host}")
        
        try:
            response = await call_next(request)
            logger.info(f"Response Sent: {response.status_code} for {request.url.path}")
            return response
        except Exception as e:
            # Avoid logging detailed exception traces to stdout directly if they could contain sensitive code or tokens,
            # but log the high-level error message securely.
            logger.error(f"Uncaught Exception during {request.url.path}: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "An internal server error occurred."}
            )
