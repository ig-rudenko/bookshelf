from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Publisher, Book


async def get_publishers(
    session: AsyncSession, search: str | None = None, user: User | None = None
) -> list[str]:
    query: Select[tuple[str]] = select(Publisher.name).select_from(Book).join(Publisher)
    if search is not None:
        query = query.where(Publisher.name.ilike(f"%{search}%"))
    if user is not None:
        query = query.where(Book.user_id == user.id)
    else:
        query = query.where(Book.private.is_(False))
    results = await session.execute(query)
    return list(results.scalars().all())
