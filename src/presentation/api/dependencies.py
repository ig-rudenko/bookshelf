from functools import cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.books.handlers import BookmarksQueryHandler, BookmarksCommandHandler, BookQueryHandler
from src.application.books.services import RecentBookService
from src.application.services.cache import AbstractCache
from src.application.services.storage import AbstractStorage
from src.application.users.handlers import (
    JWTHandler,
    RegisterUserHandler,
    ForgotPasswordHandler,
    ResetPasswordHandler,
)
from src.domain.common.unit_of_work import UnitOfWork
from src.infrastructure.auth.hashers import BcryptPasswordHasher, PasswordHasherProtocol
from src.infrastructure.auth.token_service import JWTService
from src.infrastructure.cache import RedisCache, InMemoryCache
from src.infrastructure.celery import celery_task_manager
from src.infrastructure.db.session_manager import get_session
from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.media_storage import S3Storage, LocalStorage
from src.infrastructure.settings import settings, MediaStorageEnum


@cache
def get_hasher() -> PasswordHasherProtocol:
    return BcryptPasswordHasher()


@cache
def get_jwt_token_service() -> JWTService:
    return JWTService(
        secret=settings.jwt_secret,
        access_expiration_minutes=settings.jwt_access_token_expire_minutes,
        refresh_expiration_days=settings.jwt_refresh_token_expire_days,
    )


@cache
def get_storage() -> AbstractStorage:
    if settings.media_storage_type == MediaStorageEnum.s3:
        return S3Storage(bucket_name=settings.BUCKET_NAME, endpoint_url=settings.S3_ENDPOINT_URL)
    return LocalStorage(settings.media_root)


@cache
def get_cache_service() -> AbstractCache:
    """Возвращает кэш в зависимости от настроек приложения"""
    if settings.REDIS_HOST:
        return RedisCache(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
        )
    else:
        return InMemoryCache()


def get_recent_book_service(cache_: AbstractCache = Depends(get_cache_service)):
    return RecentBookService(cache=cache_)


def get_unit_of_work(session: AsyncSession = Depends(get_session, use_cache=True)) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session)


def get_token_auth_handler(
    session: AsyncSession = Depends(get_session, use_cache=True),
    hasher: BcryptPasswordHasher = Depends(get_hasher),
    token_service: JWTService = Depends(get_jwt_token_service),
) -> JWTHandler:
    return JWTHandler(uow=SqlAlchemyUnitOfWork(session), hasher=hasher, token_service=token_service)


def get_register_handler(
    session: AsyncSession = Depends(get_session, use_cache=True),
    hasher: BcryptPasswordHasher = Depends(get_hasher),
) -> RegisterUserHandler:
    return RegisterUserHandler(uow=SqlAlchemyUnitOfWork(session), hasher=hasher)


def get_forgot_password_handler(session: AsyncSession = Depends(get_session, use_cache=True)):
    return ForgotPasswordHandler(uow=SqlAlchemyUnitOfWork(session), task_manager=celery_task_manager)


def get_reset_password_handler(
    session: AsyncSession = Depends(get_session, use_cache=True),
    hasher: BcryptPasswordHasher = Depends(get_hasher),
):
    return ResetPasswordHandler(uow=SqlAlchemyUnitOfWork(session), hasher=hasher)


def get_bookmark_query_handler(session: AsyncSession = Depends(get_session, use_cache=True)):
    return BookmarksQueryHandler(uow=SqlAlchemyUnitOfWork(session))


def get_bookmark_command_handler(session: AsyncSession = Depends(get_session, use_cache=True)):
    return BookmarksCommandHandler(uow=SqlAlchemyUnitOfWork(session))


def get_book_query_handler(
    session: AsyncSession = Depends(get_session, use_cache=True),
    storage: AbstractStorage = Depends(get_storage),
    recent_book_service: RecentBookService = Depends(get_recent_book_service),
):
    return BookQueryHandler(
        uow=SqlAlchemyUnitOfWork(session),
        storage=storage,
        recent_book_service=recent_book_service,
    )
