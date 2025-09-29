from dataclasses import dataclass, field
from datetime import datetime
from typing import Self

from ..common.exceptions import ValidationError


@dataclass(slots=True, kw_only=True)
class BookValue:
    id: int
    preview: str = ""


@dataclass(slots=True, kw_only=True)
class Bookshelf:
    id: int
    name: str
    description: str
    user_id: int
    private: bool
    created_at: datetime = field(default_factory=datetime.now)
    books: list[BookValue] = field(default_factory=list)

    def __post_init__(self):
        if self.id < 0:
            raise ValidationError(f"Bookshelf id must be greater than 0, got {self.id}")
        if self.user_id < 0:
            raise ValidationError(f"User id must be greater than 0, got {self.user_id}")
        if not self.name:
            raise ValidationError("Bookshelf name must be provided")

    @classmethod
    def create(
        cls, name: str, description: str, user_id: int, books: list[BookValue], private: bool = False
    ) -> Self:
        return cls(id=0, name=name, description=description, user_id=user_id, books=books, private=private)


@dataclass(slots=True, kw_only=True)
class BookshelfFilter:
    viewer_id: int | None = None
    search: str | None = None
    is_private: bool | None = None
    user_id: int | None = None
    book_id: int | None = None
    page: int
    page_size: int
