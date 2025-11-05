from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from loguru import logger

from src.domain.common.exceptions import (
    MultipleResultsFoundError,
    NotFoundError,
    ObjectNotFoundError,
    PermissionDeniedError,
    UniqueError,
    ValidationError,
)


async def repository_error_handler(request: Request, exc: Exception):
    """Обрабатывает ошибки репозиториев"""
    if isinstance(exc, ObjectNotFoundError):
        return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})
    if isinstance(exc, UniqueError):
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": f"Object with same `{exc.field}` already exists"},
        )
    if isinstance(exc, MultipleResultsFoundError):
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": "Multiple objects found"}
        )

    logger.error("Repository error", exc_info=exc)
    return ORJSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(exc)})


async def domain_error_handler(request: Request, exc: Exception):
    """Обрабатывает ошибки доменной логики"""
    if isinstance(exc, NotFoundError):
        return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})
    if isinstance(exc, ValidationError):
        return ORJSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": str(exc)})
    if isinstance(exc, PermissionDeniedError):
        return ORJSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)})

    logger.error("Domain error", exc_info=exc)
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"}
    )


async def storage_error_handler(request: Request, exc: Exception):
    return ORJSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Файл книги не найден"})


async def auth_error_handler(request: Request, exc: Exception):
    """Возвращает ответ с ошибкой 401, если ошибка авторизации"""
    return ORJSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )
