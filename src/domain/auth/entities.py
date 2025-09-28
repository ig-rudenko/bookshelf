from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel


class TokenPayload(BaseModel):
    type: Literal["access", "refresh"]
    sub: UUID
    exp: int
    iat: int


@dataclass(frozen=True, slots=True, kw_only=True)
class JWToken:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID
    token: str
    token_hash: str
    revoked: bool
    expire_at: datetime
    issued_at: datetime

    payload: TokenPayload | None = None
