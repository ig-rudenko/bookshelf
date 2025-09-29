from abc import ABC, abstractmethod

from .entities import BookReadHistory, BookReadHistoryFilter


class BookReadHistoryRepository(ABC):
    """Интерфейс репозитория для BookReadHistory."""

    @abstractmethod
    async def get_last_for_user(self, book_id: int, user_id: int) -> BookReadHistory: ...

    @abstractmethod
    async def add(self, book_history: BookReadHistory) -> BookReadHistory: ...

    @abstractmethod
    async def get_filtered(self, filter_: BookReadHistoryFilter) -> tuple[list[BookReadHistory], int]: ...

    @abstractmethod
    async def update(self, book_history: BookReadHistory) -> BookReadHistory: ...

    @abstractmethod
    async def delete_for_user(self, user_id: int, book_id: int) -> None: ...

    @abstractmethod
    async def delete_for_book(self, book_id: int) -> None: ...
