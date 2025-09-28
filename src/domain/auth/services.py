from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from ..common.exceptions import (
    InvalidTokenError,
    ObjectNotFoundError,
    RefreshTokenRevokedError,
)
from .entities import JWToken, TokenPayload
from .repository import RefreshTokenRepository


@dataclass(frozen=True, slots=True, kw_only=True)
class TokenPair:
    access: JWToken
    refresh: JWToken


class TokenService(ABC):

    @abstractmethod
    async def create_token_pair(self, user_id: UUID) -> TokenPair: ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> TokenPair: ...

    @abstractmethod
    async def get_user_id(self, token: str) -> UUID: ...

    @staticmethod
    @abstractmethod
    def get_token_hash(token: str) -> str: ...

    @abstractmethod
    def get_payload(self, token: str) -> TokenPayload:
        """
        Raises:
            InvalidTokenError: Если токен не валиден
        """


class AuthService:
    def __init__(self, token_service: TokenService, refresh_repo: RefreshTokenRepository):
        self.token_service = token_service
        self.refresh_repo = refresh_repo

    async def login(self, user_id: UUID) -> TokenPair:
        pair = await self.token_service.create_token_pair(user_id)
        await self.refresh_repo.add(pair.refresh)
        return pair

    async def refresh(self, refresh_token: str) -> TokenPair:
        """
        Raises:
            RefreshTokenRevokedError: если токен уже был использован
            InvalidTokenError: если токен не валиден
        """
        payload = self.token_service.get_payload(refresh_token)
        if not payload.type != "refresh":
            raise InvalidTokenError("Refresh token is not valid. It is not a 'refresh' token")

        token_hash: str = self.token_service.get_token_hash(refresh_token)
        try:
            token = await self.refresh_repo.get_by_hash(token_hash)
        except ObjectNotFoundError as exc:
            raise RefreshTokenRevokedError("Refresh token not found or already revoked") from exc

        if token.revoked:
            raise RefreshTokenRevokedError("Refresh token not found or already revoked")

        pair = await self.token_service.refresh_token(refresh_token)
        try:
            await self.refresh_repo.revoke(token_hash)
        except ObjectNotFoundError as exc:
            raise RefreshTokenRevokedError("Refresh token not found or already revoked") from exc
        return pair

    async def logout(self, user_id: UUID) -> None:
        await self.refresh_repo.revoke_all_for_user(user_id)
