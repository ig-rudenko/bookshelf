from pydantic import Field

from .base import CamelSerializerModel, CamelAliasModel


class PublisherSchema(CamelSerializerModel):
    id: int
    name: str = Field(..., max_length=128)


class TagSchema(CamelSerializerModel):
    id: int
    name: str = Field(..., max_length=128)


class CreateBookSchema(CamelAliasModel):
    publisher: str = Field(..., max_length=128)

    title: str = Field(..., max_length=254)
    authors: str = Field(..., max_length=254)
    description: str
    year: int
    private: bool
    language: str = Field(..., max_length=128)
    tags: list[str]


class BookSchema(CamelSerializerModel):
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


class BooksListSchema(CamelSerializerModel):
    books: list[BookSchema]
    total_count: int
    current_page: int
    max_pages: int
    per_page: int
