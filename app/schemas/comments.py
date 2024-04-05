from datetime import datetime

from .base import CamelSerializerModel, CamelAliasModel


class CommentCreateUpdateSchema(CamelAliasModel):
    text: str


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
