from functools import reduce

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession


async def query_count(query, session: AsyncSession) -> int:
    """Определяет количество записей запроса"""
    count_query = query.limit(None).offset(None).with_only_columns(func.count())
    count_result = await session.execute(count_query)
    counts_list = list(count_result.scalars())
    return reduce(lambda x, y: x + y, counts_list) if counts_list else 0
