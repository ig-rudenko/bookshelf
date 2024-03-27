from sqlalchemy import select

from ..models import User
from ..database.connector import db_conn
from ..schemas.users import UserCreate
from ..services.encrypt import encrypt_password


async def get_user(**kwargs) -> User:
    async with db_conn.session as session:
        filters = [getattr(User, key) == value for key, value in kwargs.items()]
        result = await session.execute(select(User).where(*filters))
        return result.scalar_one()


async def create_user(user: UserCreate) -> User:
    user_data = user.model_dump()
    user_data["password"] = encrypt_password(user_data["password"])
    obj = User(**user_data)
    async with db_conn.session as session:
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
    return obj
