from fastapi import HTTPException
from sqlalchemy import select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import Book, User


async def check_book_owner_permission(session: AsyncSession, user_id: int, book: int | Book):
    """
    Если пользователь не является владельцем книги, выбрасывает исключение.
    :param session: :class:`AsyncSession` объект сессии.
    :param user_id: ID пользователя.
    :param book: ID книги или объект книги.

    :raises HTTPException:  403 Forbidden :class:`HTTPException`.
    :raises ValueError:     book must be int or Book.
    """
    if isinstance(book, int):
        result = await session.execute(select(Book.user_id).where(Book.id == book))
        book_owner_id: int | None = result.scalar_one_or_none()
    elif isinstance(book, Book):
        book_owner_id = book.user_id
    else:
        raise ValueError("book must be int or Book")

    if book_owner_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")

    elif book_owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на доступ к этой книге"
        )


async def check_non_private_or_owner_book_permission(
    session: AsyncSession, user: User | None, book: int | Book
):
    """
    Если книга является приватной, и пользователь не является владельцем, выбрасывает исключение.

    :param session: :class:`AsyncSession` объект сессии.
    :param user: Объект пользователя или None.
    :param book: ID книги или объект книги.

    :raises HTTPException:
        - 403 Forbidden :class:`HTTPException` (У вас нет прав на доступ к этой книге).
        - 404 Not Found :class:`HTTPException` (Книга не найдена).
    :raises ValueError:     book must be int or Book.

    """
    if isinstance(book, int):
        query: Select[tuple[int, bool]] = select(Book.user_id, Book.private).where(Book.id == book)
        result = list(await session.execute(query))
        if result:
            book_owner_id, book_private = result[0]
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")
    elif isinstance(book, Book):
        book_owner_id = book.user_id
        book_private = book.private
    else:
        raise ValueError("book must be int or Book")
    if book_private and (user is None or book_owner_id != user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав на доступ к этой книге"
        )
