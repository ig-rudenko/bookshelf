from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..schemas.users import UserCreateSchema
from ..services.encrypt import encrypt_password


async def create_user(session: AsyncSession, user: UserCreateSchema) -> User:
    user_data = user.model_dump()
    user_data["password"] = encrypt_password(user_data["password"])
    obj = User(**user_data)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj
