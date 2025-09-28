from abc import ABC, abstractmethod

from ..books.repository import BookRepository
from ..bookshelves.repository import BookshelfRepository
from ..comments.repository import CommentRepository
from ..history.repository import BookReadHistoryRepository
from ..users.repository import UserRepository


class UnitOfWork(ABC):
    """Контракт для Unit of Work."""

    @property
    @abstractmethod
    def books(self) -> BookRepository: ...

    @property
    @abstractmethod
    def bookshelves(self) -> BookshelfRepository: ...

    @property
    @abstractmethod
    def comments(self) -> CommentRepository: ...

    @property
    @abstractmethod
    def book_read_history(self) -> BookReadHistoryRepository: ...

    @property
    @abstractmethod
    def users(self) -> UserRepository: ...
