from sqlalchemy import select, Select, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Publisher, Book


async def get_publishers(session: AsyncSession, search: str | None = None) -> list[str]:
    """
    Получение списка издателей книг по названию.

    :param session: :class:`AsyncSession` объект сессии.
    :param search: Строка поиска.
    :return: Список издателей.
    """
    query: Select[tuple[str]] = select(distinct(Publisher.name)).select_from(Book).join(Publisher)
    if search is not None:
        query = query.where(Publisher.name.ilike(f"%{search}%"))
    results = await session.execute(query)
    return list(results.scalars().all())
