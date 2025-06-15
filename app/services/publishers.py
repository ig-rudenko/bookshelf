from sqlalchemy import select, Select, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Publisher, Book
from app.orm.query_formats import filter_books_by_user


async def get_publishers(
    session: AsyncSession, search: str | None = None, user_id: int | None = None
) -> list[str]:
    """
    Получение списка издателей книг по названию.

    :param session: :class:`AsyncSession` объект сессии.
    :param search: Строка поиска.
    :param user_id: Идентификатор пользователя.
    :return: Список издателей.
    """
    query: Select[tuple[str]] = select(distinct(Publisher.name)).select_from(Book).join(Publisher)
    if search is not None:
        query = query.where(Publisher.name.ilike(f"%{search}%"))

    query = filter_books_by_user(query, user_id)

    results = await session.execute(query)
    return list(results.scalars().all())


async def get_authors(
    session: AsyncSession, search: str | None = None, user_id: int | None = None
) -> list[str]:
    """
    Получение списка авторов книг по названию.

    :param session: :class:`AsyncSession` объект сессии.
    :param search: Строка поиска.
    :param user_id: Идентификатор пользователя.
    :return: Список авторов.
    """
    query: Select[tuple[str]] = select(distinct(Book.authors)).limit(10)
    if search is not None:
        query = query.where(Book.authors.ilike(f"%{search}%"))

    query = filter_books_by_user(query, user_id)

    results = await session.execute(query)
    return list(results.scalars().all())


async def get_or_create_publisher(
    session: AsyncSession, publisher_name: str, *, commit: bool = True
) -> Publisher:
    """Находит или создает издательство по названию"""
    query = select(Publisher).where(Publisher.name.ilike(publisher_name))
    result = await session.execute(query)
    result.unique()
    publisher = result.scalar_one_or_none()
    if publisher is None:
        publisher = Publisher(name=publisher_name)
        session.add(publisher)
        if commit:
            await session.commit()
            await session.refresh(publisher)

    return publisher
