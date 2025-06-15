from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession


async def query_count(query, session: AsyncSession) -> int:
    """
    Определяет количество записей запроса
    Для подсчета кол-ва записей без фильтра не работает.
    """
    count_query = query.with_only_columns(func.count()).limit(None).offset(None).group_by(None).order_by(None)
    count_result = await session.execute(count_query)
    return count_result.scalar_one()
