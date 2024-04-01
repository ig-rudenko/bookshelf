from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.exc import IntegrityError, NoResultFound

from app import models
from ..crud.users import create_user
from ..schemas.auth import TokenPair, RefreshToken, AccessToken
from ..schemas.users import User, UserCreate, UserCredentials
from ..services.auth import (
    create_jwt_token_pair,
    get_current_user,
    CredentialsException,
    refresh_access_token,
)
from ..services.encrypt import validate_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/users", response_model=User)
async def register_user(user: UserCreate):
    try:
        return await create_user(user)
    except IntegrityError:
        raise HTTPException(status_code=422, detail="User already exists")


@router.post("/token", response_model=TokenPair)
async def get_tokens(user: UserCredentials):
    """Получение пары JWT"""
    try:
        user_model = await models.User.get(username=user.username)
    except NoResultFound:
        raise CredentialsException

    if not validate_password(user.password, user_model.password):
        raise CredentialsException

    return create_jwt_token_pair(user_id=user_model.id)


@router.post("/token/refresh", response_model=AccessToken)
def refresh_token(token: RefreshToken):
    """Получение нового access token через refresh token"""
    return AccessToken(accessToken=refresh_access_token(token.refresh_token))


@router.get("/myself", response_model=User)
def verify_jwt(user: models.User = Depends(get_current_user)):
    return user
