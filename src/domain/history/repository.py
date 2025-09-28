from abc import ABC, abstractmethod

from .entities import BookReadHistory
from ..comments.entities import CommentFilter


class BookReadHistoryRepository(ABC):
    """Интерфейс репозитория для BookReadHistory."""

    @abstractmethod
    async def get_for_user(self, book_id: int, user_id: int) -> BookReadHistory: ...

    @abstractmethod
    async def get_filtered(self, filter_: CommentFilter) -> tuple[list[BookReadHistory], int]: ...

    @abstractmethod
    async def add(self, book_history: BookReadHistory) -> BookReadHistory: ...

    @abstractmethod
    async def update(self, book_history: BookReadHistory) -> BookReadHistory: ...

    @abstractmethod
    async def delete(self, book_id: int) -> None: ...
