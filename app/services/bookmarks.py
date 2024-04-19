from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.models import favorite_books_association, books_read_association, Book
from app.schemas.books import BooksSchemaPaginated
from app.services.books import get_paginated_books


async def get_favorite_books(user_id: int, session: AsyncSession, paginator: dict) -> BooksSchemaPaginated:
    query = (
        select(Book, favorite_books_association.columns.id)
        .join(favorite_books_association)
        .where(favorite_books_association.columns.user_id == user_id)
    )
    return await get_paginated_books(session, query, paginator)


async def get_read_books(user_id: int, session: AsyncSession, paginator: dict) -> BooksSchemaPaginated:
    query = (
        select(Book, books_read_association.columns.id)
        .join(books_read_association)
        .where(books_read_association.columns.user_id == user_id)
    )
    return await get_paginated_books(session, query, paginator)


async def mark_favorite(session: AsyncSession, user: User, book: Book, favorite: bool):
    has_favorite = book in await user.await_attr.favorites

    if favorite and not has_favorite:
        user.favorites.append(book)
        await session.commit()
    if not favorite and has_favorite:
        user.favorites.remove(book)
        await session.commit()


async def mark_read(session: AsyncSession, user: User, book: Book, read: bool):
    book_already_read = book in await user.await_attr.books_read

    if read and not book_already_read:
        user.books_read.append(book)
        await session.commit()
    if not read and book_already_read:
        user.books_read.remove(book)
        await session.commit()
