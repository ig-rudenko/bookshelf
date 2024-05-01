from fastapi import Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from ..orm.session_manager import get_session
from ..schemas.auth import (
    TokenPair,
    RefreshToken,
    AccessToken,
    ForgotPasswordSchema,
    ForgotPasswordResponseSchema,
    ResetPasswordSchema,
)
from ..schemas.users import UserSchema, UserCreateSchema, UserCredentialsSchema
from ..services.aaa import (
    create_jwt_token_pair,
    get_current_user,
    refresh_access_token,
)
from ..services.aaa.captcha import verify_captcha
from ..services.aaa.reset_password import (
    verify_forgot_password_email_send,
    reset_password,
    get_user_from_token,
)
from ..services.aaa.users import create_user, get_user_by_credentials
from ..services.celery import send_reset_password_email_task
from ..settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/users", response_model=UserSchema)
async def register_user(
    user: UserCreateSchema, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        if await verify_captcha(user.recaptcha_token, request.client.host):
            return await create_user(session, user)
        return HTTPException(status_code=422, detail="Вы не прошли проверку для регистрации")
    except IntegrityError:
        raise HTTPException(status_code=422, detail="User already exists")


@router.post("/token", response_model=TokenPair)
async def get_tokens(user_data: UserCredentialsSchema, session: AsyncSession = Depends(get_session)):
    """Получение пары JWT"""
    user = await get_user_by_credentials(session, user_data.username, user_data.password)
    return create_jwt_token_pair(user_id=user.id)


@router.post("/token/refresh", response_model=AccessToken)
def refresh_token(token: RefreshToken):
    """Получение нового access token через refresh token"""
    return AccessToken(access_token=refresh_access_token(token.refresh_token))


@router.get("/myself", response_model=UserSchema)
def verify_jwt(user: models.User = Depends(get_current_user)):
    return user


@router.post("/forgot-password", response_model=ForgotPasswordResponseSchema)
async def forgot_password_api_view(
    data: ForgotPasswordSchema, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        if await verify_forgot_password_email_send(session, data, request_ip=request.client.host):
            send_reset_password_email_task.delay(data.email)
            return ForgotPasswordResponseSchema(
                detail=f"Письмо отправлено от имени {settings.EMAIL_FROM}, "
                f"проверьте письмо на указанном вами адресе (также в папке Спам)",
                success=True,
            )
    except HTTPException as exc:
        return ForgotPasswordResponseSchema(detail=exc.detail, success=False)

    return ForgotPasswordResponseSchema(
        detail="Вы не прошли проверку для отправки письма, попробуйте еще раз", success=False
    )


@router.get("/reset-password/verify/{token}", response_model=UserSchema)
async def reset_password_verify_api_view(token: str, session: AsyncSession = Depends(get_session)):
    return await get_user_from_token(session, token)


@router.post("/reset-password")
async def reset_password_api_view(data: ResetPasswordSchema, session: AsyncSession = Depends(get_session)):
    await reset_password(session, data.token, data.password1, data.password2)
