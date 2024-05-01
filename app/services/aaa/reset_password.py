from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.auth import ForgotPasswordSchema
from app.services.aaa.captcha import verify_captcha
from app.services.aaa.jwt import create_reset_password_token, decode_reset_password_token
from app.services.email import get_email_service
from app.services.encrypt import encrypt_password
from app.settings import settings


async def verify_forgot_password_email_send(
    session: AsyncSession, data: ForgotPasswordSchema, *, request_ip: str
) -> bool:
    """
    Проверяет, существует ли пользователь с таким email, а также проверяет капчу через токен.
    :param session: :class:`AsyncSession` - объект сессии.
    :param data: Данные для проверки.
    :param request_ip: IP адрес пользователя.
    :raises HTTPException: 404, 403.
    """
    try:
        user = await User.get(session, email=data.email)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Пользователь с таким email не найден")
    if user.reset_passwd_email_datetime and user.reset_passwd_email_datetime > datetime.now() - timedelta(
        minutes=2
    ):
        raise HTTPException(
            status_code=403,
            detail="Повторную отправку письма на смену пароля можно выполнить только через 2 минуты",
        )

    verify = await verify_captcha(data.recaptcha_token, request_ip)
    if verify:
        user.reset_passwd_email_datetime = datetime.now()
        await user.save(session)
    return verify


async def send_reset_password_email(email: str):
    """
    Отправляет письмо на смену пароля.
    :param email: Email пользователя.
    :return: True, если письмо отправлено.
    """

    secret_token = create_reset_password_token(email=email)
    forget_url_link = f"https://it-bookshelf.ru/reset-password/{secret_token}"

    email_body = {
        "link_expire_minutes": settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES,
        "reset_link": forget_url_link,
    }
    subject = "Сброс пароля на сайте it-bookshelf.ru"
    get_email_service().send_reset_password_email(email, subject, email_body)


async def get_user_from_token(session: AsyncSession, token: str) -> User:
    """
    Получает пользователя по токену.
    :param session: :class:`AsyncSession` - объект сессии.
    :param token: Токен для сброса пароля.
    :return: :class:`User`.
    :raises HTTPException: 404, 403.
    """
    email = decode_reset_password_token(token)
    if email is None:
        raise HTTPException(status_code=403, detail="Неверный токен для сброса пароля")
    try:
        user = await User.get(session, email=email)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Пользователь с таким email не найден")
    return user


async def reset_password(session: AsyncSession, token: str, password1: str, password2: str) -> None:
    """
    Сбрасывает пароль пользователя.
    :param session: :class:`AsyncSession` - объект сессии.
    :param token: Токен для сброса пароля.
    :param password1: Пароль пользователя.
    :param password2: Подтверждение пароля пользователя.
    :return: True, если пароль сброшен.
    """
    if password1 != password2:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")

    user = await get_user_from_token(session, token)
    user.password = encrypt_password(password1)
    await user.save(session)
