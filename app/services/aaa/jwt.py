import os
from datetime import timedelta, datetime, UTC

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.schemas.auth import TokenPair
from app.services.aaa.exc import (
    CredentialsException,
    InvalidAccessTokenException,
    InvalidRefreshTokenException,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "i9i3902849209323m009sfhs90dh")
ALGORITHM = "HS512"
USER_IDENTIFIER = "user_id"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_HOURS = 24 * 30


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
        raise _get_invalid_token_exc(token_type)

    if payload.get("type") != token_type:
        raise _get_invalid_token_exc(token_type)
    if payload.get(USER_IDENTIFIER) is None:
        raise CredentialsException
    return payload


def _get_invalid_token_exc(token_type: str) -> HTTPException:
    """
    Возвращает исключение в зависимости от типа токена.
    """
    if token_type == "access":
        return InvalidAccessTokenException
    else:
        return InvalidRefreshTokenException
