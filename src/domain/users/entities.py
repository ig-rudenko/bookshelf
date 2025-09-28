from dataclasses import dataclass, field
from datetime import datetime

from ..common.exceptions import ValidationError


@dataclass(slots=True, kw_only=True)
class User:
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    password: str
    is_superuser: bool
    is_staff: bool
    is_active: bool
    date_join: datetime = field(default_factory=datetime.now)
    last_login: datetime | None = None
    reset_passwd_email_datetime: datetime | None = None

    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        is_superuser: bool = False,
        is_staff: bool = False,
        is_active: bool = True,
    ):
        username = username.strip()
        email = email.strip()
        password_hash = password.strip()
        if not username or not email or not password_hash:
            raise ValidationError("Username, email and password cannot be empty")
        return cls(
            id=0,
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_superuser=is_superuser,
            is_staff=is_staff,
            is_active=is_active,
            last_login=None,
        )
