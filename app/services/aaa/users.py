import re
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.orm.session_manager import get_session
from .exc import CredentialsException
from .jwt import oauth2_scheme, _get_token_payload, USER_IDENTIFIER
from ..encrypt import encrypt_password
from ...schemas.users import UserCreateSchema


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


async def create_user(session: AsyncSession, user: UserCreateSchema) -> User:
    user_data = user.model_dump()
    user_data["password"] = encrypt_password(user_data["password"])
    obj = User(**user_data)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj
