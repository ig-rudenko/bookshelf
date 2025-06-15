from fastapi import Depends, HTTPException
from starlette import status

from app.models import User
from app.services.aaa import get_current_user


def superuser_required(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required",
        )
    return current_user
