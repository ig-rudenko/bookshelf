from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from ..orm.session_manager import get_session
from ..schemas.auth import TokenPair, RefreshToken, AccessToken
from ..schemas.users import UserSchema, UserCreateSchema, UserCredentialsSchema
from ..services.aaa import (
    create_jwt_token_pair,
    get_current_user,
    refresh_access_token,
)
from ..services.aaa.users import create_user, get_user_by_credentials

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/users", response_model=UserSchema)
async def register_user(user: UserCreateSchema, session: AsyncSession = Depends(get_session)):
    try:
        return await create_user(session, user)
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
