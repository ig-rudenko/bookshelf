from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Book
from app.orm.session_manager import get_session
from app.schemas.books import BooksSchemaPaginated
from app.services.aaa import get_current_user
from app.services.bookmarks import (
    get_favorite_books,
    mark_favorite,
    mark_read,
    get_read_books,
    get_favorite_books_count,
    get_read_books_count,
)
from app.services.books import get_book
from app.services.paginator import paginator_query

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.get("/favorite", status_code=status.HTTP_200_OK, response_model=BooksSchemaPaginated)
async def get_favorite_books_view(
    paginator: dict = Depends(paginator_query),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await get_favorite_books(session=session, user_id=user.id, paginator=paginator)


@router.get("/favorite/count", status_code=status.HTTP_200_OK, response_model=int)
async def get_favorite_books_count_view(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await get_favorite_books_count(session=session, user_id=user.id)


@router.get("/read", status_code=status.HTTP_200_OK, response_model=BooksSchemaPaginated)
async def get_read_books_view(
    paginator: dict = Depends(paginator_query),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await get_read_books(session=session, user_id=user.id, paginator=paginator)


@router.get("/read/count", status_code=status.HTTP_200_OK, response_model=int)
async def get_read_books_count_view(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await get_read_books_count(session=session, user_id=user.id)


@router.post("/{book_id}/favorite", status_code=status.HTTP_200_OK)
async def mark_book_favorite(
    book_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    book: Book = await get_book(session, book_id)
    await mark_favorite(session, user, book, favorite=True)


@router.delete("/{book_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def unmark_book_favorite(
    book_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    book: Book = await get_book(session, book_id)
    await mark_favorite(session, user, book, favorite=False)


@router.post("/{book_id}/read", status_code=status.HTTP_200_OK)
async def mark_book_read(
    book_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    book: Book = await get_book(session, book_id)
    await mark_read(session, user, book, read=True)


@router.delete("/{book_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def unmark_book_read(
    book_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    book: Book = await get_book(session, book_id)
    await mark_read(session, user, book, read=False)
