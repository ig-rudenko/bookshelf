from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Book, User


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
