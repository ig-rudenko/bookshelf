import re

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.users.dto import UserDTO
from src.application.users.services import get_user_by_token
from src.domain.common.exceptions import ObjectNotFoundError, ValidationError
from src.domain.common.unit_of_work import UnitOfWork
from src.infrastructure.auth.token_service import JWTService, decode_reset_password_token
from src.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

from .dependencies import get_jwt_token_service, get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session, use_cache=True),
    token_service: JWTService = Depends(get_jwt_token_service),
) -> UserDTO:
    """Получение текущего пользователя по токену аутентификации."""
    uow = SqlAlchemyUnitOfWork(session)

    try:
        user = await get_user_by_token(token, token_service=token_service, uow=uow)
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Inactive user")
    except (ValueError, ValidationError, ObjectNotFoundError) as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return user


async def get_admin_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session, use_cache=True),
    token_service: JWTService = Depends(get_jwt_token_service),
) -> UserDTO:
    uow = SqlAlchemyUnitOfWork(session)
    try:
        if user := await get_user_by_token(token, token_service=token_service, uow=uow):
            if not (user.is_active and user.is_superuser):
                raise HTTPException(status_code=403, detail="Forbidden")
            return user
        raise HTTPException(status_code=401, detail="Unauthorized")
    except (ValueError, ValidationError, ObjectNotFoundError) as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


async def get_user_or_none(
    authorization: str | None = Header(None),
    session: AsyncSession = Depends(get_session, use_cache=True),
    token_service: JWTService = Depends(get_jwt_token_service),
) -> UserDTO | None:
    """
    Получение текущего пользователя по токену аутентификации.

    :param authorization: Значение заголовка HTTP (Authorization).
    :param session: :class:`AsyncSession` объект сессии.
    :param token_service: Объект сервиса для работы с токенами.
    :return: Объект пользователя :class:`User` или :class:`None`.
    :raises CredentialsException: Если пользователь не найден.
    """
    if authorization and (token_match := re.match(r"Bearer (\S+)", authorization)) is not None:
        try:
            return await get_current_user(token_match.group(1), session, token_service)
        except HTTPException:
            pass
    return None


async def get_user_by_reset_password_token(token: str, uow: UnitOfWork) -> UserDTO:
    email = decode_reset_password_token(token)
    if email is None:
        raise HTTPException(detail="Неверный токен для сброса пароля", status_code=403)
    try:
        async with uow:
            user = await uow.users.get_by_email(email)
            return UserDTO(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                is_staff=user.is_staff,
                date_join=user.date_join,
            )
    except ObjectNotFoundError as exc:
        raise HTTPException(detail="Неверный токен для сброса пароля", status_code=403) from exc


def superuser_required(current_user: UserDTO = Depends(get_current_user)) -> UserDTO:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required",
        )
    return current_user
