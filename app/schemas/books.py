from pydantic import BaseModel, Field


class PublisherSchema(BaseModel):
    id: int
    name: str = Field(..., max_length=128)

    class Config:
        from_attributes = True


class TagSchema(BaseModel):
    id: int
    name: str = Field(..., max_length=128)

    class Config:
        from_attributes = True


class CreateBookSchema(BaseModel):
    publisher: str = Field(..., max_length=128)

    title: str = Field(..., max_length=254)
    authors: str = Field(..., max_length=254)
    description: str
    year: int
    private: bool
    language: str = Field(..., max_length=128)
    tags: list[str]


class BookSchema(BaseModel):
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

    class Config:
        from_attributes = True


class BooksListSchema(BaseModel):
    books: list[BookSchema]
    totalCount: int
    currentPage: int
    maxPages: int
    perPage: int
