from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from uvicorn import server

from src.domain.common.exceptions import RepositoryError, DomainError, AuthorizationError
from src.infrastructure.db.session_manager import db_manager
from src.infrastructure.logging import setup_logger
from src.infrastructure.settings import settings
from src.presentation.api.exception_handlers import (
    auth_error_handler,
    domain_error_handler,
    repository_error_handler,
)
from src.presentation.api.handlers.admin import router as admin_router
from src.presentation.api.handlers.auth import router as auth_router
from src.presentation.api.handlers.bookmarks import router as bookmark_router
from src.presentation.api.handlers.books import router as book_router
from src.presentation.api.handlers.bookshelves import router as bookshelf_router
from src.presentation.api.handlers.comments import router as comment_router
from src.presentation.api.handlers.history import router as history_router


@asynccontextmanager
async def startup(app_instance: FastAPI):
    db_manager.init(settings.database_url, echo=settings.database_echo)
    logger.info("Database initialized")
    yield
    logger.info("Closing database")
    await db_manager.close()
    logger.info("Database closed")


setup_logger(settings.log_level)
server.logger = logger
app = FastAPI(lifespan=startup)
# app.add_middleware(LoggingMiddleware, logger=logger, ignore_paths=["/ping"])  # noqa

# Регистрируем глобальные обработчики ошибок.
app.add_exception_handler(RepositoryError, repository_error_handler)
app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(AuthorizationError, auth_error_handler)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(book_router, prefix="/api/v1")
app.include_router(bookmark_router, prefix="/api/v1")
app.include_router(comment_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")
app.include_router(bookshelf_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


@app.get("/ping", tags=["health"])
async def status():
    return {"message": "pong"}
