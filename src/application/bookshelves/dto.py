from dataclasses import dataclass
from datetime import datetime
from typing import Self

from src.domain.bookshelves.entities import Bookshelf


@dataclass(slots=True, kw_only=True)
class BookshelfElementDTO:
    id: int
    preview: str


@dataclass(slots=True, kw_only=True)
class BookshelfDTO:
    id: int
    name: str
    description: str
    created_at: datetime
    user_id: int
    private: bool
    books: list[BookshelfElementDTO]

    @classmethod
    def from_domain(cls, data: Bookshelf) -> Self:
        return cls(
            id=data.id,
            name=data.name,
            description=data.description,
            created_at=data.created_at,
            user_id=data.user_id,
            private=data.private,
            books=[
                BookshelfElementDTO(
                    id=book.id,
                    preview=book.preview,
                )
                for book in data.books
            ],
        )
