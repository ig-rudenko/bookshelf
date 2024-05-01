from typing import Self, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class Manager:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> Self:
        obj = cls(**kwargs)
        session.add(obj)  # Добавляем объект в его таблицу.
        await session.commit()  # Подтверждаем.
        await session.refresh(obj)  # Обновляем атрибуты у объекта, чтобы получить его primary key.
        return obj

    @classmethod
    async def get(cls, session: AsyncSession, **kwargs) -> Self:
        filters = [getattr(cls, key) == value for key, value in kwargs.items()]
        query = select(cls).where(*filters)
        result = await session.execute(query)
        result.unique()
        return result.scalar_one()

    @classmethod
    async def exists(cls, session: AsyncSession, **kwargs) -> bool:
        filters = [getattr(cls, key) == value for key, value in kwargs.items()]
        query = select(getattr(cls, "id")).where(*filters)
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None

    @classmethod
    async def all(cls, session: AsyncSession) -> Sequence[Self]:
        result = await session.execute(select(cls))
        return result.scalars().all()

    async def save(self, session: AsyncSession) -> None:
        session.add(self)
        await session.commit()
        await session.refresh(self)

    async def delete(self, session: AsyncSession) -> None:
        await session.delete(self)
        await session.commit()
