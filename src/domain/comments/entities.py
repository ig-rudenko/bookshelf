from dataclasses import dataclass
from datetime import datetime

from src.domain.common.exceptions import ValidationError


@dataclass(slots=True, kw_only=True)
class Comment:
    id: int
    user_id: int
    book_id: int
    text: str
    created_at: datetime

    def __post_init__(self):
        if self.user_id < 0:
            raise ValidationError(f"User ID must be positive. Got `{self.user_id}` instead.")
        if self.book_id < 0:
            raise ValidationError(f"Book ID must be positive. Got `{self.book_id}` instead.")


@dataclass(slots=True, kw_only=True)
class CommentFilter:
    search: str | None = None
    book_id: int | None = None
    user_id: int | None = None
    page: int
    page_size: int
