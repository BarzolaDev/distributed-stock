import redis
import os
from fastapi import Request
from fastapi.responses import JSONResponse

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.from_url(REDIS_URL)

RATE_LIMIT = 10
WINDOW = 60

async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host
    key = f"rate_limit:{ip}"
    
    current = r.incr(key)
    
    if current == 1:
        r.expire(key, WINDOW)
    
    if current > RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"}
        )
    
    return await call_next(request)
