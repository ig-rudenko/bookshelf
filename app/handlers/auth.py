from fastapi.exceptions import HTTPException

from fastapi import Depends
from sqlalchemy.exc import IntegrityError, NoResultFound
from fastapi.routing import APIRouter

from app import models
from ..crud.users import create_user, get_user
from ..schemas.users import User, UserCreate, UserCredentials
from ..schemas.auth import TokenPair
from ..services.auth import create_jwt_token_pair, get_current_user, CredentialsException
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
        user_model = await get_user(username=user.username)
    except NoResultFound:
        raise CredentialsException

    if not validate_password(user.password, user_model.password):
        raise CredentialsException

    return create_jwt_token_pair(user_id=user_model.id)


@router.get("/myself", response_model=User)
def verify_jwt(user: models.User = Depends(get_current_user)):
    return user
