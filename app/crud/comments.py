from functools import reduce
from typing import TypeVar

from sqlalchemy import select, Select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Comment, User
from app.schemas.comments import CommentUserSchema, CommentCreateUpdateSchema, UserSchema


async def create_comment(
    session: AsyncSession, data: CommentCreateUpdateSchema, book_id: int, user_id: int
) -> Comment:
    data.text = data.text.strip()
    comment = await Comment.create(session, **data.model_dump(), book_id=book_id, user_id=user_id)
    await session.commit()
    return comment


QT = TypeVar("QT", bound=Select)


def filter_params(query: QT, query_params: dict):
    if query_params["page"] and query_params["per_page"]:
        per_page = query_params["per_page"]
        page = query_params["page"]
        query = query.offset((page - 1) * per_page).limit(per_page)
    return query


async def get_comments(
    session: AsyncSession, book_id: int, query_params: dict
) -> tuple[list[CommentUserSchema], int]:
    query = (
        select(Comment, User.username)
        .join(User)
        .where(Comment.book_id == book_id)
        .order_by(Comment.created_at.desc())
    )
    query = filter_params(query, query_params)
    result = []
    for comment, username in await session.execute(query):
        result.append(
            CommentUserSchema(
                id=comment.id,
                text=comment.text,
                created_at=comment.created_at,
                user=UserSchema(id=comment.user_id, username=username),
            )
        )
    comments_count = await _get_comments_count_for_query(
        session,
        filter_params(select(func.count(Comment.id)), query_params),
    )
    return result, comments_count


async def _get_comments_count_for_query(session: AsyncSession, query) -> int:
    """Определяет количество книг для запроса"""
    count_query = query.limit(None).offset(None)
    count_result = await session.execute(count_query)
    counts_list = list(count_result.scalars())
    return reduce(lambda x, y: x + y, counts_list) if counts_list else 0
