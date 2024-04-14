from fastapi import APIRouter, Depends, status, Query
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.comments import get_comments, create_comment
from app.models import Book, Comment
from app.orm.session_manager import get_session
from app.schemas.comments import (
    CommentCreateUpdateSchema,
    CommentSchema,
    CommentUserSchema,
    UserSchema,
    CommentsListSchema,
)
from app.services.auth import get_user_or_none, get_current_user
from app.services.permissions import check_non_private_or_owner_book_permission

router = APIRouter(prefix="/comments", tags=["comments"])


def comments_query_params(
    page: int = Query(1, gt=0, description="Номер страницы"),
    per_page: int = Query(25, gte=1, alias="per-page", description="Количество элементов на странице"),
):
    return {"page": page, "per_page": per_page}


@router.get("/book/{book_id}", response_model=CommentsListSchema)
async def get_book_comments_view(
    book_id: int,
    query_params: dict = Depends(comments_query_params),
    session: AsyncSession = Depends(get_session),
    user=Depends(get_user_or_none),
):
    await check_non_private_or_owner_book_permission(session, user, book_id)
    comments_schema, total_count = await get_comments(session, book_id, query_params)

    return CommentsListSchema(
        comments=comments_schema,
        total_count=total_count,
        current_page=query_params["page"],
        max_pages=total_count // query_params["per_page"] or 1,
        per_page=query_params["per_page"],
    )


@router.post("/book/{book_id}", status_code=status.HTTP_201_CREATED, response_model=CommentUserSchema)
async def create_book_comment_view(
    book_id: int,
    comment_data: CommentCreateUpdateSchema,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    if not await Book.exists(session, id=book_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")

    comment = await create_comment(session, comment_data, book_id, user.id)
    return CommentUserSchema(
        id=comment.id,
        text=comment.text,
        created_at=comment.created_at,
        user=UserSchema.model_validate(user),
    )


@router.put("/{comment_id}", response_model=CommentSchema)
async def update_comment_view(
    comment_id: int,
    comment_data: CommentCreateUpdateSchema,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
) -> Comment:
    try:
        comment = await Comment.get(session, id=comment_id)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден")
    else:
        if comment.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на редактирование")
        comment.text = comment_data.text
        await comment.save(session)
        return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_view(
    comment_id: int,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
) -> None:
    try:
        comment = await Comment.get(session, id=comment_id)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден")
    else:
        if comment.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на удаление")
        await comment.delete(session)
