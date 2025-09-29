from fastapi import APIRouter, Request, HTTPException, Depends

from src.application.users.commands import (
    RegisterUserCommand,
    LoginUserCommand,
    ForgotPasswordCommand,
    ResetPasswordCommand,
)
from src.application.users.dto import UserDTO
from src.application.users.handlers import (
    RegisterUserHandler,
    JWTHandler,
    ForgotPasswordHandler,
    ResetPasswordHandler,
)
from src.domain.common.exceptions import ObjectNotFoundError, AuthorizationError
from src.domain.common.unit_of_work import UnitOfWork
from src.infrastructure.auth.captcha import verify_captcha
from ..auth import get_current_user, get_user_by_reset_password_token
from ..dependencies import (
    get_register_handler,
    get_token_auth_handler,
    get_forgot_password_handler,
    get_unit_of_work,
    get_reset_password_handler,
)
from ..helpers import get_client_ip
from ..schemas.auth import (
    TokenPairSchema,
    RefreshTokenSchema,
    ForgotPasswordResponseSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
)
from ..schemas.users import UserSchema, UserCreateSchema, UserCredentialsSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/users", response_model=UserSchema)
async def register_user(
    user: UserCreateSchema,
    request: Request,
    register_handler: RegisterUserHandler = Depends(get_register_handler),
):
    if not await verify_captcha(user.recaptcha_token, remote_ip=get_client_ip(request)):
        raise HTTPException(status_code=422, detail="Вы не прошли проверку для регистрации")

    user = await register_handler.handle(
        RegisterUserCommand(
            username=user.username,
            password=user.password,
            email=str(user.email),
        )
    )
    return user


@router.post("/token", response_model=TokenPairSchema)
async def get_token_pair(
    user_data: UserCredentialsSchema, jwt_handler: JWTHandler = Depends(get_token_auth_handler)
):
    cmd = LoginUserCommand(username=user_data.username, password=user_data.password)
    try:
        token_pair = await jwt_handler.handle_obtain_token(cmd)
        return TokenPairSchema(access_token=token_pair.access, refresh_token=token_pair.refresh)
    except (ObjectNotFoundError, AuthorizationError) as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/token/refresh", response_model=TokenPairSchema)
async def refresh_tokens(
    token_data: RefreshTokenSchema, jwt_handler: JWTHandler = Depends(get_token_auth_handler)
):
    token_pair = await jwt_handler.handle_refresh_token(token_data.refresh_token)
    return TokenPairSchema(access_token=token_pair.access, refresh_token=token_pair.refresh)


@router.get("/myself", response_model=UserSchema)
def verify_jwt(user: UserDTO = Depends(get_current_user)):
    """Проверка JWT"""
    return user


@router.post("/forgot-password", response_model=ForgotPasswordResponseSchema)
async def forgot_password_api_view(
    data: ForgotPasswordSchema,
    request: Request,
    handler: ForgotPasswordHandler = Depends(get_forgot_password_handler),
):
    if not await verify_captcha(data.recaptcha_token, remote_ip=get_client_ip(request)):
        return ForgotPasswordResponseSchema(
            detail="Вы не прошли проверку для отправки письма, попробуйте еще раз", success=False
        )
    await handler.handle(ForgotPasswordCommand(email=data.email))
    return ForgotPasswordResponseSchema(
        detail=f"Письмо отправлено проверьте на указанном вами адресе (также в папке Спам)",
        success=True,
    )


@router.get("/reset-password/verify/{token}", response_model=UserSchema)
async def reset_password_verify_api_view(token: str, uow: UnitOfWork = Depends(get_unit_of_work)):
    """Проверка токена для сброса пароля"""
    return await get_user_by_reset_password_token(token, uow)


@router.post("/reset-password")
async def reset_password_api_view(
    data: ResetPasswordSchema, handler: ResetPasswordHandler = Depends(get_reset_password_handler)
):
    """Сброс пароля пользователя"""
    if data.password1 != data.password2:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")

    user = await get_user_by_reset_password_token(token=data.token, uow=handler.uow)
    await handler.handle(ResetPasswordCommand(user_id=user.id, password=data.password1))
