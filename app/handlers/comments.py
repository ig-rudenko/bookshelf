from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Book, Comment, User
from ..orm.session_manager import get_session
from ..schemas.comments import (
    CommentCreateUpdateSchema,
    CommentSchema,
    CommentUserSchema,
    CommentsPaginateSchema,
)
from ..services.aaa import get_user_or_none, get_current_user
from ..services.comments import create_comment, get_comments
from ..services.paginator import paginator_query
from ..services.permissions import check_non_private_or_owner_book_permission

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/book/{book_id}", response_model=CommentsPaginateSchema)
async def get_book_comments_view(
    book_id: int,
    query_params: dict = Depends(paginator_query),
    session: AsyncSession = Depends(get_session),
    user: Optional[User] = Depends(get_user_or_none),
):
    """
    Возвращает список комментариев к книге.
    :param book_id: Идентификатор книги.
    :param query_params: Параметры для постраничного отображения.
    :param session: Сессия базы данных.
    :param user: Пользователь либо None.
    """

    await check_non_private_or_owner_book_permission(session, user, book_id)
    return await get_comments(session, book_id, query_params)


@router.post("/book/{book_id}", status_code=status.HTTP_201_CREATED, response_model=CommentUserSchema)
async def create_book_comment_view(
    book_id: int,
    comment_data: CommentCreateUpdateSchema,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    """
    Создание комментария к книге.
    :param book_id: Идентификатор книги.
    :param comment_data: Данные комментария.
    :param session: Сессия базы данных.
    :param user: Пользователь :class:`User`.
    """
    if not await Book.exists(session, id=book_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")

    return await create_comment(session, comment_data, user, book_id)


@router.put("/{comment_id}", response_model=CommentSchema)
async def update_comment_view(
    comment_id: int,
    comment_data: CommentCreateUpdateSchema,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
) -> Comment:
    """
    Редактирование комментария.
    :param comment_id: Идентификатор комментария.
    :param comment_data: Данные комментария.
    :param session: Сессия базы данных.
    :param user: Пользователь :class:`User`.
    """

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
    """
    Удаление комментария.
    :param comment_id: Идентификатор комментария.
    :param session: Сессия базы данных.
    :param user: Пользователь :class:`User`.
    """

    try:
        comment = await Comment.get(session, id=comment_id)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден")
    else:
        if comment.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав на удаление")
        await comment.delete(session)
