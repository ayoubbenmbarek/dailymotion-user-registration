from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Database
from app.routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    await Database.connect()
    yield
    await Database.disconnect()


app = FastAPI(
    title="Dailymotion User Registration API",
    description="A user registration API with email verification",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(users.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
