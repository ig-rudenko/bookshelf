from dataclasses import dataclass
from datetime import datetime
from typing import Self

from src.domain.users.entities import UserDetail


@dataclass(frozen=True, slots=True, kw_only=True)
class UserDTO:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str

    is_active: bool
    is_superuser: bool
    is_staff: bool

    date_join: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class UserDetailDTO(UserDTO):
    favorites_count: int = 0
    read_count: int = 0
    recently_read_count: int = 0

    @classmethod
    def from_domain(cls, user: UserDetail) -> Self:
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            is_staff=user.is_staff,
            date_join=user.date_join,
            favorites_count=user.favorites_count,
            read_count=user.read_count,
            recently_read_count=user.recently_read_count,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class JWTokenDTO:
    access: str
    refresh: str
