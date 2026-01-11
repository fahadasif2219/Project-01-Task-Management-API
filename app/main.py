"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import engine, init_db
from app.routers.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    await init_db()
    yield


app = FastAPI(
    title="Task Management API",
    description="AI-400 Class-1 Project: Task Management with Network Operations Skills",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(tasks_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint with database connectivity test."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "ok",
        "database": db_status,
    }
