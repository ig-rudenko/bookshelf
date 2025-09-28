from dataclasses import dataclass

from ..services.storage import FileProtocol


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateBookCommand:
    book_file: FileProtocol
    user_id: int
    publisher: str
    title: str
    authors: str
    description: str
    year: int
    private: bool
    language: str
    tags: list[str]


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateBookCommand:
    book_file: FileProtocol
    book_id: int
    publisher: str
    title: str
    authors: str
    description: str
    year: int
    private: bool
    language: str
    tags: list[str]
