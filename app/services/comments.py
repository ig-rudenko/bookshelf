from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import query_count
from app.models import User, Comment
from app.schemas.comments import (
    CommentCreateUpdateSchema,
    CommentUserSchema,
    UserSchema,
    CommentsPaginateSchema,
)
from app.services.paginator import paginate


async def create_comment(
    session: AsyncSession, comment_data: CommentCreateUpdateSchema, user: User, book_id: int
) -> CommentUserSchema:
    comment = await Comment.create(session, text=comment_data.text.strip(), book_id=book_id, user_id=user.id)
    return CommentUserSchema(
        id=comment.id,
        text=comment.text,
        created_at=comment.created_at,
        user=UserSchema.model_validate(user),
    )


async def get_comments(session: AsyncSession, book_id: int, paginator: dict) -> CommentsPaginateSchema:
    query = (
        select(Comment, User.username)
        .join(User)
        .where(Comment.book_id == book_id)
        .group_by(Comment)
        .order_by(Comment.created_at.desc())
    )
    query = paginate(query, page=paginator["page"], per_page=paginator["per_page"])

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
    comments_count = await query_count(query, session)

    return CommentsPaginateSchema(
        comments=result,
        total_count=comments_count,
        current_page=paginator["page"],
        max_pages=comments_count // paginator["per_page"] or 1,
        per_page=paginator["per_page"],
    )
