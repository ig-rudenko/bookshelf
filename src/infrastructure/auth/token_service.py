import hashlib
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

import jwt

from src.domain.auth.entities import JWToken, TokenPayload
from src.domain.auth.services import TokenPair, TokenService
from src.domain.common.exceptions import InvalidTokenError


class JWTService(TokenService):
    def __init__(self, secret: str, access_expiration_minutes: int = 60, refresh_expiration_days: int = 30):
        self._secret = secret
        self.access_expiration_minutes = access_expiration_minutes
        self.refresh_expiration_days = refresh_expiration_days

    async def get_user_id(self, token: str) -> UUID:
        payload = self.get_payload(token)
        return payload.sub

    async def create_token_pair(self, user_id: UUID) -> TokenPair:
        access, access_payload = self._create_token(user_id, "access")
        refresh, refresh_payload = self._create_token(user_id, "refresh")
        return TokenPair(
            access=JWToken(
                token=access,
                token_hash=self.get_token_hash(access),
                user_id=user_id,
                issued_at=datetime.fromtimestamp(access_payload.iat, UTC),
                expire_at=datetime.fromtimestamp(access_payload.exp, UTC),
                revoked=False,
                payload=access_payload,
            ),
            refresh=JWToken(
                token=refresh,
                token_hash=self.get_token_hash(refresh),
                user_id=user_id,
                issued_at=datetime.fromtimestamp(refresh_payload.iat, UTC),
                expire_at=datetime.fromtimestamp(refresh_payload.exp, UTC),
                revoked=False,
                payload=refresh_payload,
            ),
        )

    async def refresh_token(self, refresh_token: str) -> TokenPair:
        payload = self.get_payload(refresh_token)
        if payload.type != "refresh":
            raise InvalidTokenError(f"Invalid token type. Expected 'refresh', got '{payload.type}'.")
        return await self.create_token_pair(payload.sub)

    def get_payload(self, token: str) -> TokenPayload:
        try:
            payload = TokenPayload(**jwt.decode(token, self._secret, algorithms=["HS256"]))
        except jwt.ExpiredSignatureError:
            raise InvalidTokenError("Token expired")
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Invalid token")
        return payload

    def _create_token(self, user_id: UUID, type_: Literal["access", "refresh"]) -> tuple[str, TokenPayload]:
        exp = datetime.now(UTC)
        if type_ == "access":
            exp += timedelta(minutes=self.access_expiration_minutes)
        elif type_ == "refresh":
            exp += timedelta(days=self.refresh_expiration_days)

        payload = TokenPayload(
            sub=user_id,
            exp=int(exp.timestamp()),
            type=type_,
            iat=int(datetime.now(UTC).timestamp()),
        )

        enc_token = jwt.encode(payload.model_dump(mode="json"), self._secret, algorithm="HS256")
        return enc_token, payload

    @staticmethod
    def get_token_hash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
