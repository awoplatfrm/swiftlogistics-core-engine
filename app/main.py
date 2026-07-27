from fastapi import FastAPI
from app.routers import shipments, auth
from contextlib import asynccontextmanager
from app.database import ASYNC_ENGINE, Base
import app.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with ASYNC_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Logistics API", lifespan=lifespan)

app.include_router(shipments.router, prefix="/api/v1")
app.include_router(shipments.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Welcome to SwiftLogistics API",
        "docs": "Visit /docs for the interactive API documentation",
        "status": "online",
    }
