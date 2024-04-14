from datetime import datetime

from pydantic import Field

from .base import CamelSerializerModel, CamelAliasModel


class CommentCreateUpdateSchema(CamelAliasModel):
    text: str = Field(..., min_length=1, max_length=1024)


class CommentSchema(CamelSerializerModel):
    id: int
    text: str
    created_at: datetime
    book_id: int


class UserSchema(CamelSerializerModel):
    id: int
    username: str


class CommentUserSchema(CamelSerializerModel):
    id: int
    text: str
    created_at: datetime
    user: UserSchema


class CommentsListSchema(CamelSerializerModel):
    comments: list[CommentUserSchema]
    total_count: int
    current_page: int
    max_pages: int
    per_page: int
