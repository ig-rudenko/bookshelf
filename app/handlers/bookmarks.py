from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.books import get_book
from app.models import User, Book
from app.orm.session_manager import get_session
from app.schemas.books import BookSchema
from app.services.auth import get_current_user
from app.services.bookmarks import mark_favorite, mark_read

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.get("/favorite", status_code=status.HTTP_200_OK, response_model=list[BookSchema])
async def get_favorite_books(user: User = Depends(get_current_user)):
    return await user.await_attr.favorites


@router.get("/read", status_code=status.HTTP_200_OK, response_model=list[BookSchema])
async def get_favorite_books(user: User = Depends(get_current_user)):
    return await user.await_attr.books_read


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