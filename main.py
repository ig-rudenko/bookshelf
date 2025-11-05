from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from loguru import logger
from uvicorn import server

from src.application.services.storage import AbstractStorage
from src.domain.common.exceptions import AuthorizationError, DomainError, RepositoryError
from src.infrastructure.celery import register_tasks
from src.infrastructure.db.session_manager import db_manager
from src.infrastructure.settings import settings
from src.presentation.api.exception_handlers import (
    auth_error_handler,
    domain_error_handler,
    repository_error_handler,
    storage_error_handler,
)
from src.presentation.api.handlers.admin import router as admin_router
from src.presentation.api.handlers.auth import router as auth_router
from src.presentation.api.handlers.bookmarks import router as bookmark_router
from src.presentation.api.handlers.books import router as book_router
from src.presentation.api.handlers.bookshelves import router as bookshelf_router
from src.presentation.api.handlers.comments import router as comment_router
from src.presentation.api.handlers.history import router as history_router
from src.presentation.middlewares.logging import LoggingMiddleware


@asynccontextmanager
async def startup(app_instance: FastAPI):
    db_manager.init(
        settings.database_url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
    )
    await register_tasks()
    logger.info("Database initialized")
    yield
    logger.info("Closing database")
    await db_manager.close()
    logger.info("Database closed")


server.logger = logger  # type: ignore
app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=startup,
)

logging_middleware = LoggingMiddleware(logger)
app.middleware("http")(logging_middleware.dispatch)

# Регистрируем глобальные обработчики ошибок.
app.add_exception_handler(RepositoryError, repository_error_handler)
app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(AuthorizationError, auth_error_handler)
app.add_exception_handler(AbstractStorage.FileNotFoundError, storage_error_handler)

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
