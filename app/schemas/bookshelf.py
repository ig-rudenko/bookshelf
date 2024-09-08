from datetime import datetime

from pydantic import Field

from .base import CamelAliasModel, CamelSerializerModel


class CreateUpdateBookshelfSchema(CamelAliasModel):
    name: str = Field(..., min_length=3, max_length=128)
    description: str = Field(..., max_length=1000)
    books: list[int] = Field(..., min_length=1)


class BookshelfSchema(CreateUpdateBookshelfSchema):
    id: int
    created_at: datetime = Field(..., alias="createdAt")
    books: list[int]


class BookshelfSchemaSchemaPaginated(CamelSerializerModel):
    """
    Схема для представления списка книг (без описания).
    Содержит информацию о количестве всех записей, текущей странице,
    максимальное кол-во страниц, количество записей на одной странице"""

    books: list[BookshelfSchema]
    total_count: int
    current_page: int
    max_pages: int
    per_page: int
