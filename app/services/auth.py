import os
import re
from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from ..models import User
from ..orm.session_manager import get_session
from ..schemas.auth import TokenPair

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
# Замените на случайный секретный ключ
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "i9i3902849209323m009sfhs90dh")
ALGORITHM = "HS512"
USER_IDENTIFIER = "user_id"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_HOURS = 24 * 30

CredentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

InvalidRefreshTokenException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid refresh token",
    headers={"WWW-Authenticate": "Bearer"},
)

InvalidAccessTokenException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid access token",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_jwt_token_pair(user_id: int) -> TokenPair:
    """
    Создает пару токенов: access_token, refresh_token.
    :param user_id: Идентификатор пользователя.
    :return: :class:`TokenPair`.
    """
    access_token = _create_jwt_token(
        {USER_IDENTIFIER: user_id, "type": "access"},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = _create_jwt_token(
        {USER_IDENTIFIER: user_id, "type": "refresh"},
        timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS),
    )
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session, use_cache=True),
) -> User:
    """
    Получение текущего пользователя по токену аутентификации.

    :param token: Токен пользователя.
    :param session: :class:`AsyncSession` объект сессии.
    :return: Объект пользователя :class:`User`.
    :raises CredentialsException: Если пользователь не найден.
    """
    payload = _get_token_payload(token, "access")
    try:
        user = await User.get(session, id=payload[USER_IDENTIFIER])
    except NoResultFound:
        raise CredentialsException

    return user


async def get_user_or_none(
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_session, use_cache=True),
) -> User | None:
    """
    Получение текущего пользователя по токену аутентификации.

    :param authorization: Значение заголовка HTTP (Authorization).
    :param session: :class:`AsyncSession` объект сессии.
    :return: Объект пользователя :class:`User` или :class:`None`.
    :raises CredentialsException: Если пользователь не найден.
    """
    if authorization:
        if token_match := re.match(r"Bearer (\S+)", authorization):
            try:
                return await get_current_user(token_match.group(1), session)
            except HTTPException:
                return None
    return None


def refresh_access_token(refresh_token: str) -> str:
    """
    Создает новый access_token на основе переданного refresh_token.
    """
    payload = _get_token_payload(refresh_token, "refresh")

    return _create_jwt_token(
        {USER_IDENTIFIER: payload[USER_IDENTIFIER], "type": "access"},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def _create_jwt_token(data: dict, delta: timedelta) -> str:
    """
    Создает JWT токен.
    :param data: Полезная нагрузка.
    :param delta: Время жизни токена.
    :return: Закодированный токен.
    """
    expires_delta = datetime.now(UTC) + delta
    data.update({"exp": expires_delta})
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def _get_token_payload(token: str, token_type: str) -> dict:
    """
    Возвращает payload токена.

    :param token: Закодированный токен.
    :param token_type: Тип токена (access или refresh).
    :return: Словарь полезной нагрузки.
    :raises CredentialsException: Если токен недействителен.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise get_invalid_token_exc(token_type)

    if payload.get("type") != token_type:
        raise get_invalid_token_exc(token_type)
    if payload.get(USER_IDENTIFIER) is None:
        raise CredentialsException
    return payload


def get_invalid_token_exc(token_type: str) -> HTTPException:
    """
    Возвращает исключение в зависимости от типа токена.
    """
    if token_type == "access":
        return InvalidAccessTokenException
    else:
        return InvalidRefreshTokenException
