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


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateFavoriteCommand:
    user_id: int
    book_id: int
    favorite: bool


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateReadCommand:
    user_id: int
    book_id: int
    read: bool
