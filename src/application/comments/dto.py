from dataclasses import dataclass
from datetime import datetime
from typing import Self

from src.domain.comments.entities import Comment


@dataclass
class CommentDTO:
    id: int
    username: str
    user_id: int
    text: str
    created_at: datetime

    @classmethod
    def from_domain(cls, comment: Comment) -> Self:
        return cls(
            id=comment.id,
            username=comment.username,
            user_id=comment.user_id,
            text=comment.text,
            created_at=comment.created_at,
        )
