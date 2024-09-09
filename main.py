from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from uvicorn import server

from app.handlers.auth import router as auth_router
from app.handlers.bookmarks import router as bookmark_router
from app.handlers.books import router as book_router
from app.handlers.bookshelf import router as bookshelf_router
from app.handlers.comments import router as comment_router
from app.handlers.user_data import router as user_data_router
from app.middlewares.logging import LoggingMiddleware
from app.orm.session_manager import db_manager
from app.services.logging import setup_logger
from app.settings import settings


@asynccontextmanager
async def startup(app_instance: FastAPI):
    db_manager.init(settings.database_url)
    logger.info("Database initialized")
    yield
    logger.info("Closing database")
    await db_manager.close()
    logger.info("Database closed")


setup_logger(settings.log_level)
server.logger = logger
app = FastAPI(lifespan=startup)
app.add_middleware(LoggingMiddleware, logger=logger)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(book_router, prefix="/api/v1")
app.include_router(bookmark_router, prefix="/api/v1")
app.include_router(comment_router, prefix="/api/v1")
app.include_router(user_data_router, prefix="/api/v1")
app.include_router(bookshelf_router, prefix="/api/v1")


@app.get("/ping", tags=["health"])
async def status():
    return {"message": "pong"}
