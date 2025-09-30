from dataclasses import dataclass

from src.application.users.dto import UserDTO


@dataclass(slots=True, kw_only=True)
class BookshelfCreateCommand:
    user: UserDTO
    name: str
    description: str
    private: bool
    books: list[int]


@dataclass(slots=True, kw_only=True)
class BookshelfUpdateCommand:
    id: int
    user: UserDTO
    name: str
    description: str
    private: bool
    books: list[int]


@dataclass(slots=True, kw_only=True)
class BookshelfDeleteCommand:
    id: int
    user: UserDTO
