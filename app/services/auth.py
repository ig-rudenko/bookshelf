import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import exc
from starlette import status

from ..models import User
from ..schemas.auth import TokenPair

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.environ.get(
    "JWT_SECRET_KEY", "i9i3902849209323m009sfhs90dh"
)  # Замените на случайный секретный ключ
ALGORITHM = "HS512"
USER_IDENTIFIER = "user_id"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_HOURS = 24

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


def create_jwt_token_pair(user_id: str) -> TokenPair:
    """
    Создает пару токенов: access_token, refresh_token.
    """
    access_token = _create_jwt_token(
        {USER_IDENTIFIER: user_id, "type": "access"},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = _create_jwt_token(
        {USER_IDENTIFIER: user_id, "type": "refresh"},
        timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS),
    )
    return TokenPair(accessToken=access_token, refreshToken=refresh_token)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Получение текущего пользователя"""
    payload = _get_token_payload(token, "access")

    try:
        user = await User.get(id=payload[USER_IDENTIFIER])
    except exc.NoResultFound:
        raise CredentialsException

    return user


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
    expires_delta = datetime.utcnow() + delta
    data.update({"exp": expires_delta})
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def _get_token_payload(token: str, token_type: str) -> dict:
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
    if token_type == "access":
        return InvalidAccessTokenException
    else:
        return InvalidRefreshTokenException
