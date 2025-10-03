from fastapi import Request, status
from fastapi.responses import JSONResponse

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
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})
    if isinstance(exc, UniqueError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": f"Object with same `{exc.field}` already exists"},
        )
    if isinstance(exc, MultipleResultsFoundError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": "Multiple objects found"}
        )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(exc)})


async def domain_error_handler(request: Request, exc: Exception):
    """Обрабатывает ошибки доменной логики"""
    if isinstance(exc, NotFoundError):
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})
    if isinstance(exc, ValidationError):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": str(exc)})
    if isinstance(exc, PermissionDeniedError):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"}
    )


async def auth_error_handler(request: Request, exc: Exception):
    """Возвращает ответ с ошибкой 401, если ошибка авторизации"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )
