from dataclasses import dataclass
from typing import Self

from src.domain.books.entities import Book


@dataclass(slots=True, kw_only=True)
class PublisherDTO:
    id: int
    name: str


@dataclass(slots=True, kw_only=True)
class BookDTO:
    id: int
    user_id: int
    publisher: PublisherDTO
    title: str
    preview_image: str
    authors: str
    pages: int
    size: int
    year: int
    private: bool
    language: str
    tags: list[str]

    @classmethod
    def from_domain(cls, book: Book) -> Self:
        return cls(
            id=book.id,
            user_id=book.user_id,
            title=book.title,
            publisher=PublisherDTO(
                id=book.publisher.id,
                name=book.publisher.name,
            ),
            preview_image=book.preview_image,
            authors=book.authors,
            pages=book.pages,
            size=book.size,
            year=book.year,
            private=book.private,
            language=book.language,
            tags=book.tags,
        )


@dataclass(slots=True, kw_only=True)
class BookshelfLinkDTO:
    id: int
    name: str
    private: bool


@dataclass(slots=True, kw_only=True)
class TagDTO:
    id: int
    name: str


@dataclass(slots=True, kw_only=True)
class DetailBookDTO(BookDTO):
    description: str
    favorite: bool
    read: bool
    bookshelves: list[BookshelfLinkDTO]
    tags: list[TagDTO]
