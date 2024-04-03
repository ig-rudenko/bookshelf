from pydantic import Field

from .base import BaseConfigModel


class PublisherSchema(BaseConfigModel):
    id: int
    name: str = Field(..., max_length=128)


class TagSchema(BaseConfigModel):
    id: int
    name: str = Field(..., max_length=128)


class CreateBookSchema(BaseConfigModel):
    publisher: str = Field(..., max_length=128)

    title: str = Field(..., max_length=254)
    authors: str = Field(..., max_length=254)
    description: str
    year: int
    private: bool
    language: str = Field(..., max_length=128)
    tags: list[str]


class BookSchema(BaseConfigModel):
    id: int
    user_id: int

    title: str = Field(..., max_length=254)
    preview_image: str = Field(..., max_length=128)
    authors: str = Field(..., max_length=254)
    description: str
    pages: int
    size: int
    year: int
    private: bool
    language: str = Field(..., max_length=128)
    tags: list[TagSchema]
    publisher: PublisherSchema


class BooksListSchema(BaseConfigModel):
    books: list[BookSchema]
    totalCount: int
    current_page: int
    max_pages: int
    per_page: int
