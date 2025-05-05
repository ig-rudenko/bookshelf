from typing import TypeVar

from sqlalchemy import Select

from app.models import User, Book

S = TypeVar("S", bound=Select)


def filter_books_by_user(query: S, user: User | None = None) -> S:
    if user is not None:
        return query.where(Book.private.is_(False) | (Book.private.is_(True) & (Book.user_id == user.id)))

    return query.where(Book.private.is_(False))
