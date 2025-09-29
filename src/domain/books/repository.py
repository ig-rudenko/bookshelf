from abc import ABC, abstractmethod

from .entities import Book, Tag, BookFilter, BookmarksQueryFilter


class BookRepository(ABC):
    """Интерфейс репозитория для Book."""

    @abstractmethod
    async def get_by_id(self, book_id: int) -> Book: ...

    @abstractmethod
    async def get_filtered(self, filter_: BookFilter) -> tuple[list[Book], int]: ...

    @abstractmethod
    async def add(self, book: Book) -> Book: ...

    @abstractmethod
    async def update(self, book: Book) -> Book: ...

    @abstractmethod
    async def delete(self, book_id: int) -> None: ...

    @abstractmethod
    async def get_favorite_books(self, filter_: BookmarksQueryFilter) -> tuple[list[Book], int]: ...

    @abstractmethod
    async def update_favorite_status(self, book_id: int, user_id: int, favorite: bool) -> None: ...

    @abstractmethod
    async def get_favorite_books_count(self, user_id: int) -> int: ...

    @abstractmethod
    async def is_favorite_by_user(self, book_id: int, user_id: int) -> bool: ...

    @abstractmethod
    async def get_read_books(self, filter_: BookmarksQueryFilter) -> tuple[list[Book], int]: ...

    @abstractmethod
    async def update_read_status(self, book_id: int, user_id: int, read: bool) -> None: ...

    @abstractmethod
    async def get_read_books_count(self, user_id: int) -> int: ...

    @abstractmethod
    async def is_read_by_user(self, book_id: int, user_id: int) -> bool: ...

    @abstractmethod
    async def get_book_tags(self, book_id: int) -> list[Tag]: ...
