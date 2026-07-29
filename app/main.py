from fastapi import FastAPI
from app.routers import shipments, auth
from contextlib import asynccontextmanager
from app.database import ASYNC_ENGINE, Base
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with ASYNC_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.include_router(shipments.router, prefix="/api/v1")
app.include_router(shipments.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "Visit /docs for the interactive API documentation",
        "status": "online",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
    }
