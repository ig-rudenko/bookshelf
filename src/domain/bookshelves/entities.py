from dataclasses import dataclass
from datetime import datetime

from ..books.entities import Book
from ..common.exceptions import ValidationError


@dataclass(slots=True, kw_only=True)
class Bookshelf:
    id: int
    name: str
    description: str
    created_at: datetime
    user_id: int
    private: bool

    books: list[Book]

    def __post_init__(self):
        if self.id < 0:
            raise ValidationError(f"Bookshelf id must be greater than 0, got {self.id}")
        if self.user_id < 0:
            raise ValidationError(f"User id must be greater than 0, got {self.user_id}")
        if not self.name:
            raise ValidationError(f"Bookshelf name must be provided")


@dataclass(slots=True, kw_only=True)
class BookshelfFilter:
    search: str | None = None
    is_private: bool | None = None
    user_id: int | None = None
    book_id: int | None = None
    page: int | None = None
    page_size: int | None = None
