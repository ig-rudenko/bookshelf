from dataclasses import dataclass
from datetime import datetime
from typing import Self

from src.domain.common.exceptions import ValidationError


@dataclass(slots=True, kw_only=True)
class Comment:
    id: int
    username: str
    user_id: int
    book_id: int
    text: str
    created_at: datetime

    def __post_init__(self):
        if self.user_id < 0:
            raise ValidationError(f"User ID must be positive. Got `{self.user_id}` instead.")
        if self.book_id < 0:
            raise ValidationError(f"Book ID must be positive. Got `{self.book_id}` instead.")

    @classmethod
    def create(
        cls,
        user_id: int,
        book_id: int,
        text: str,
        username: str = "",
        created_at: datetime | None = None,
    ) -> Self:
        return cls(
            id=0,
            username=username,
            user_id=user_id,
            book_id=book_id,
            text=text,
            created_at=created_at if created_at is not None else datetime.now(),
        )


@dataclass(slots=True, kw_only=True)
class CommentFilter:
    search: str | None = None
    book_id: int | None = None
    user_id: int | None = None
    page: int
    page_size: int
