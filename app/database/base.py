from typing import Self, Sequence

from sqlalchemy import select
from sqlalchemy.orm import declarative_base

from .connector import db_conn

Base = declarative_base()


class Manager:

    @classmethod
    async def create(cls, **kwargs) -> Self:
        obj = cls(**kwargs)
        async with db_conn.session as session:
            session.add(obj)            # Добавляем объект в его таблицу.
            await session.commit()      # Подтверждаем.
            await session.refresh(obj)  # Обновляем атрибуты у объекта, чтобы получить его primary key.
        return obj

    @classmethod
    async def get(cls, _id: int) -> Self:
        async with db_conn.session as session:
            result = await session.execute(
                select(cls).where(cls.id == _id)
            )
            return result.scalar_one()

    @classmethod
    async def all(cls) -> Sequence[Self]:
        async with db_conn.session as session:
            result = await session.execute(select(cls))
            return result.scalars().all()
