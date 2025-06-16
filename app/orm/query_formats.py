from typing import TypeVar

from sqlalchemy import Select

from app.models import Book, Bookshelf

S = TypeVar("S", bound=Select)


def filter_books_by_user(query: S, user_id: int | None = None) -> S:
    if user_id is not None:
        return query.where(Book.private.is_(False) | (Book.private.is_(True) & (Book.user_id == user_id)))

    return query.where(Book.private.is_(False))


def filter_bookshelf_by_user(query: S, user_id: int | None = None) -> S:
    if user_id is not None:
        return query.where(
            Bookshelf.private.is_(False) | (Bookshelf.private.is_(True) & (Bookshelf.user_id == user_id))
        )

    return query.where(Bookshelf.private.is_(False))
