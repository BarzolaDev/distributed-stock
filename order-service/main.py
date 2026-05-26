from fastapi import FastAPI
from routes.order import router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    from db.session import get_engine
    from models.order import Base
    Base.metadata.create_all(bind=get_engine())
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(router)

@app.get("/health")
def health():
    return {"service": "order", "status": "ok"}
