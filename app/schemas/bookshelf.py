from datetime import datetime

from pydantic import Field

from .base import CamelAliasModel, CamelSerializerModel


class CreateUpdateBookshelfSchema(CamelAliasModel):
    name: str = Field(..., min_length=3, max_length=128)
    description: str = Field(..., max_length=1000)
    books: list[int] = Field(..., min_length=1)


class BookshelfOneBookSchema(CamelSerializerModel):
    id: int
    preview: str


class BookshelfSchema(CamelSerializerModel):
    id: int
    name: str = Field(..., min_length=3, max_length=128)
    description: str = Field(..., max_length=1000)
    created_at: datetime
    user_id: int
    books: list[BookshelfOneBookSchema]


class BookshelfSchemaSchemaPaginated(CamelSerializerModel):
    """
    Схема для представления списка книг (без описания).
    Содержит информацию о количестве всех записей, текущей странице,
    максимальное кол-во страниц, количество записей на одной странице"""

    bookshelves: list[BookshelfSchema]
    total_count: int
    current_page: int
    max_pages: int
    per_page: int
