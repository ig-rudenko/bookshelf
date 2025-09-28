from abc import ABC, abstractmethod

from .entities import User


class UserRepository(ABC):
    """Интерфейс репозитория для User."""

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User: ...

    @abstractmethod
    async def get_filtered(self, page: int, page_size: int) -> tuple[list[User], int]: ...

    @abstractmethod
    async def add(self, user: User) -> User:
        """
        Raises:
            UniqueError: Если пользователь с таким username или email уже существует.
        """

    @abstractmethod
    async def update(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, user_id: int) -> None: ...
