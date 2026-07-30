"""
backend/rate_limiter.py
Token-Bucket Rate Limiter Middleware for HydroThermal Nexus-AI FastAPI microservices.
Protects industrial REST endpoints from DDoS and rate abuse.
"""

import time
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class SimpleRateLimiter:
    """
    In-memory Token Bucket rate limiter per client IP address.
    """

    def __init__(self, requests_per_minute: int = 120):
        self.rate = requests_per_minute
        self.capacity = requests_per_minute
        self.buckets: Dict[str, Tuple[float, float]] = {}  # ip -> (tokens, last_update)

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        if client_ip not in self.buckets:
            self.buckets[client_ip] = (self.capacity - 1.0, now)
            return True

        tokens, last_update = self.buckets[client_ip]
        # Replenish tokens based on elapsed time
        elapsed = now - last_update
        tokens = min(self.capacity, tokens + elapsed * (self.rate / 60.0))

        if tokens >= 1.0:
            self.buckets[client_ip] = (tokens - 1.0, now)
            return True

        self.buckets[client_ip] = (tokens, now)
        return False


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Starlette / FastAPI middleware enforcing IP rate limits.
    """

    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.limiter = SimpleRateLimiter(requests_per_minute=requests_per_minute)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"

        # Allow health checks and OpenAPI docs without strict rate limiting
        if request.url.path in ["/api/health", "/docs", "/openapi.json"]:
            return await call_next(request)

        if not self.limiter.is_allowed(client_ip):
            return JSONResponse(
                status_code=429,
                content={"error": "Too Many Requests", "detail": "API rate limit exceeded. Please retry in a moment."}
            )

        return await call_next(request)
