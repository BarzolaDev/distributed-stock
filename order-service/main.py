from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from routes.order import router
from middleware.rate_limiter import rate_limit_middleware
from contextlib import asynccontextmanager
from services.telemetry import setup_telemetry

@asynccontextmanager
async def lifespan(app):
    from db.session import get_engine
    from models.order import Base
    Base.metadata.create_all(bind=get_engine())
    yield

app = FastAPI(lifespan=lifespan)

setup_telemetry(app)

app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limit_middleware)

app.include_router(router)

@app.get("/health")
def health():
    return {"service": "order", "status": "ok"}
