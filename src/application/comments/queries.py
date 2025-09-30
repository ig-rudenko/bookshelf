from dataclasses import dataclass

from src.application.users.dto import UserDTO


@dataclass(slots=True, kw_only=True)
class CommentsListQuery:
    book_id: int
    user: UserDTO | None
    page: int
    page_size: int
