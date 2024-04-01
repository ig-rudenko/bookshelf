from typing import Self, Sequence

from sqlalchemy import select
from sqlalchemy.orm import declarative_base

from .connector import db_conn

Base = declarative_base()


class Manager:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    async def create(cls, **kwargs) -> Self:
        obj = cls(**kwargs)
        async with db_conn.session as session:
            session.add(obj)  # Добавляем объект в его таблицу.
            await session.commit()  # Подтверждаем.
            await session.refresh(obj)  # Обновляем атрибуты у объекта, чтобы получить его primary key.
        return obj

    @classmethod
    async def get(cls, **kwargs) -> Self:
        async with db_conn.session as session:
            filters = [getattr(cls, key) == value for key, value in kwargs.items()]
            query = select(cls).where(*filters)
            result = await session.execute(query)
            result.unique()
            return result.scalar_one()

    @classmethod
    async def all(cls) -> Sequence[Self]:
        async with db_conn.session as session:
            result = await session.execute(select(cls))
            return result.scalars().all()

    async def save(self) -> None:
        async with db_conn.session as session:
            session.add(self)
            await session.commit()
            await session.refresh(self)

    async def delete(self) -> None:
        async with db_conn.session as session:
            session.delete(self)
            await session.commit()
