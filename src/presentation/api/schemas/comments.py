from datetime import datetime
from typing import Self

from pydantic import Field

from src.application.comments.dto import CommentDTO

from .base import CamelAliasModel, CamelSerializerModel


class CommentCreateUpdateSchema(CamelAliasModel):
    text: str = Field(..., min_length=1, max_length=1024)


class UserSchema(CamelSerializerModel):
    id: int
    username: str


class CommentUserSchema(CamelSerializerModel):
    id: int
    text: str
    created_at: datetime
    user: UserSchema

    @classmethod
    def from_dto(cls, comment: CommentDTO) -> Self:
        return cls(
            id=comment.id,
            text=comment.text,
            created_at=comment.created_at,
            user=UserSchema(id=comment.user_id, username=comment.username),
        )

    @classmethod
    def from_dto_many(cls, comments: list[CommentDTO]) -> list[Self]:
        if comments:
            return [cls.from_dto(comment) for comment in comments]
        return []


class CommentsPaginateSchema(CamelSerializerModel):
    comments: list[CommentUserSchema]
    total_count: int
    current_page: int
    max_pages: int
    per_page: int
