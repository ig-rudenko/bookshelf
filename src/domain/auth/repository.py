from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.auth.entities import JWToken


class RefreshTokenRepository(ABC):
    @abstractmethod
    async def add(self, token: JWToken) -> JWToken: ...

    @abstractmethod
    async def get_by_hash(self, token_hash: str) -> JWToken:
        """
        Ищет токен по его хешу.

        Raises:
            ObjectNotFoundError: Если токена с таким хешем не существует или он был удален
        """

    @abstractmethod
    async def revoke(self, token_hash: str) -> None: ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID) -> None: ...
