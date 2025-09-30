from dataclasses import dataclass

from src.application.users.dto import UserDTO


@dataclass(slots=True, kw_only=True)
class CreateCommentCommand:
    user: UserDTO
    book_id: int
    text: str


@dataclass(slots=True, kw_only=True)
class UpdateCommentCommand:
    user: UserDTO
    comment_id: int
    text: str
