from datetime import datetime
from typing import Self

from pydantic import Field

from src.application.books.dto import BookDTO, BookWithReadPagesDTO

from .base import CamelAliasModel, CamelSerializerModel


class PublisherSchema(CamelSerializerModel):
    """Схема для представления издателя книги."""

    id: int
    name: str = Field(..., max_length=128)


class TagSchema(CamelSerializerModel):
    """Схема для представления тега книги."""

    name: str = Field(..., max_length=128)


class CreateBookSchema(CamelAliasModel):
    """Схема для создания новой книги."""

    publisher: str = Field(..., max_length=128)

    title: str = Field(..., max_length=254)
    authors: str = Field(..., max_length=254)
    description: str
    year: int
    private: bool
    language: str = Field(..., max_length=128)
    tags: list[str]


class BookSchema(CamelSerializerModel):
    """Схема для представления базовой информации о книге (без описания)."""

    id: int
    user_id: int

    title: str = Field(..., max_length=254)
    preview_image: str = Field(..., max_length=128)
    authors: str = Field(..., max_length=254)
    pages: int
    size: int
    year: int
    private: bool
    language: str = Field(..., max_length=128)
    tags: list[TagSchema]
    publisher: PublisherSchema

    @classmethod
    def from_dto(cls, book: BookDTO) -> Self:
        return cls(
            id=book.id,
            user_id=book.user_id,
            title=book.title,
            preview_image=book.preview_image,
            authors=book.authors,
            pages=book.pages,
            size=book.size,
            year=book.year,
            private=book.private,
            language=book.language,
            tags=[TagSchema(name=tag) for tag in book.tags],
            publisher=PublisherSchema(id=book.publisher.id, name=book.publisher.name),
        )


class BookSchemaWithDesc(BookSchema):
    """Схема для представления базовой информации о книге с описанием."""

    description: str

    @classmethod
    def from_dto(cls, book: BookDTO) -> Self:
        return cls(
            id=book.id,
            user_id=book.user_id,
            title=book.title,
            description=book.description,
            preview_image=book.preview_image,
            authors=book.authors,
            pages=book.pages,
            size=book.size,
            year=book.year,
            private=book.private,
            language=book.language,
            tags=[TagSchema(name=tag) for tag in book.tags],
            publisher=PublisherSchema(id=book.publisher.id, name=book.publisher.name),
        )


class BookshelfLinkSchema(CamelSerializerModel):
    id: int
    name: str
    private: bool


class BookSchemaDetail(BookSchema):
    """
    Схема для представления информации о книге с описанием,
    а также статусом избранной книги и прочитанной книги.
    """

    description: str
    favorite: bool = Field(False)
    read: bool = Field(False)
    bookshelves: list[BookshelfLinkSchema] = Field(default_factory=list)


class BooksSchemaPaginated(CamelSerializerModel):
    """
    Схема для представления списка книг (без описания).
    Содержит информацию о количестве всех записей, текущей странице,
    максимальное кол-во страниц, количество записей на одной странице"""

    books: list[BookSchema]
    total_count: int
    current_page: int
    max_pages: int
    per_page: int

    @classmethod
    def from_books_dto(
        cls, *, books: list[BookDTO], total_count: int, current_page: int, per_page: int
    ) -> Self:
        if total_count % per_page == 0:
            max_pages = total_count // per_page
        else:
            max_pages = total_count // per_page + 1

        return cls(
            books=[BookSchema.from_dto(book) for book in books],
            total_count=total_count,
            current_page=current_page,
            max_pages=max_pages,
            per_page=per_page,
        )


class BookWithReadPagesSchema(BookSchema):
    """Схема для представления информации о книге (без описания) с указанием прочитанных страниц."""

    read_pages: int = 0
    last_time_read: datetime | None = None

    @classmethod
    def from_dto_with_read_pages(cls, book: BookWithReadPagesDTO) -> Self:
        obj = cls.from_dto(book)
        obj.read_pages = book.read_pages
        obj.last_time_read = book.last_time_read
        return obj


class BooksWithReadPagesPaginatedSchema(CamelSerializerModel):
    """
    Схема для представления списка книг (без описания) с указанием прочитанных страниц.
    Содержит информацию о количестве всех записей, текущей странице,
    максимальное кол-во страниц, количество записей на одной странице"""

    books: list[BookWithReadPagesSchema]
    total_count: int
    current_page: int
    max_pages: int
    per_page: int

    @classmethod
    def from_books_dto(
        cls, *, books: list[BookWithReadPagesDTO], total_count: int, current_page: int, per_page: int
    ) -> Self:
        if total_count % per_page == 0:
            max_pages = total_count // per_page
        else:
            max_pages = total_count // per_page + 1

        return cls(
            books=[BookWithReadPagesSchema.from_dto_with_read_pages(book) for book in books],
            total_count=total_count,
            current_page=current_page,
            max_pages=max_pages,
            per_page=per_page,
        )
