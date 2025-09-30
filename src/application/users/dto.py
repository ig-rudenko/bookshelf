from dataclasses import dataclass
from datetime import datetime


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
class JWTokenDTO:
    access: str
    refresh: str
