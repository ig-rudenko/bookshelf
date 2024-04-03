from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.handlers.auth import router as auth_router
from app.handlers.books import router as book_router
from app.orm.session_manager import db_manager
from app.settings import settings


@asynccontextmanager
async def startup(app_instance: FastAPI):
    db_manager.init(settings.database_url)
    print("Database initialized")
    yield
    print("Database closed")
    await db_manager.close()


app = FastAPI(lifespan=startup)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(book_router, prefix="/api/v1")


@app.get("/ping", tags=["health"])
async def status():
    return {"message": "pong"}
