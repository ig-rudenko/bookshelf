from functools import cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.books.handlers import BookmarksQueryHandler, BookmarksCommandHandler
from src.application.users.handlers import (
    JWTHandler,
    RegisterUserHandler,
    ForgotPasswordHandler,
    ResetPasswordHandler,
)
from src.domain.common.unit_of_work import UnitOfWork
from src.infrastructure.auth.hashers import BcryptPasswordHasher, PasswordHasherProtocol
from src.infrastructure.auth.token_service import JWTService
from src.infrastructure.celery import celery_task_manager
from src.infrastructure.db.session_manager import get_session
from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.settings import settings


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
