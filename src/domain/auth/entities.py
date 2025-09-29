from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class TokenPayload(BaseModel):
    type: Literal["access", "refresh"]
    sub: int
    exp: int
    iat: int


@dataclass(frozen=True, slots=True, kw_only=True)
class JWToken:
    id: int
    user_id: int
    token: str
    token_hash: str
    revoked: bool
    expire_at: datetime
    issued_at: datetime

    payload: TokenPayload | None = None
