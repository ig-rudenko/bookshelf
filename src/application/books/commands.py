from dataclasses import dataclass

from ..services.storage import FileProtocol
from ..users.dto import UserDTO


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateBookCommand:
    user: UserDTO
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
    user: UserDTO
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
class UploadBookFileCommand:
    user: UserDTO
    book_id: int
    file: FileProtocol


@dataclass(slots=True, frozen=True, kw_only=True)
class DeleteBookCommand:
    user: UserDTO
    book_id: int


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
