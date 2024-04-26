from pydantic import Field

from .base import CamelSerializerModel, CamelAliasModel


class PublisherSchema(CamelSerializerModel):
    """Схема для представления издателя книги."""

    id: int
    name: str = Field(..., max_length=128)


class TagSchema(CamelSerializerModel):
    """Схема для представления тега книги."""

    id: int
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


class BookSchemaWithDesc(BookSchema):
    """Схема для представления базовой информации о книге с описанием."""

    description: str


class BookSchemaDetail(BookSchema):
    """
    Схема для представления информации о книге с описанием,
    а также статусом избранной книги и прочитанной книги.
    """

    description: str
    favorite: bool = Field(False)
    read: bool = Field(False)


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


class BookWithReadPagesSchema(BookSchema):
    """Схема для представления информации о книге (без описания) с указанием прочитанных страниц."""

    read_pages: int = Field(0)


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
