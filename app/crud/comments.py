from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Comment, User
from app.schemas.comments import CommentUserSchema, CommentCreateUpdateSchema, UserSchema


async def create_comment(
    session: AsyncSession, data: CommentCreateUpdateSchema, book_id: int, user_id: int
) -> Comment:
    comment = await Comment.create(session, **data.model_dump(), book_id=book_id, user_id=user_id)
    await session.commit()
    return comment


async def get_comments(session: AsyncSession, book_id: int) -> list[CommentUserSchema]:
    query = (
        select(Comment, User.username)
        .join(User)
        .where(Comment.book_id == book_id)
        .order_by(Comment.created_at.desc())
    )
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
    return result
