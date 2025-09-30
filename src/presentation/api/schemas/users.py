from datetime import datetime

from pydantic import EmailStr, Field

from .base import CamelAliasModel, CamelSerializerModel


class UserSchema(CamelSerializerModel):
    id: int
    username: str = Field(..., min_length=2, max_length=150)
    email: EmailStr = Field(..., max_length=254)
    first_name: str | None = Field(None, max_length=150)
    last_name: str | None = Field(None, max_length=150)
    is_superuser: bool
    is_staff: bool
    date_join: datetime


class UserCredentialsSchema(CamelAliasModel):
    username: str = Field(..., max_length=150)
    password: str = Field(..., max_length=128)


class UserCreateSchema(CamelAliasModel):
    username: str = Field(..., min_length=2, max_length=150)
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=50)
    recaptcha_token: str


class UserDetailSchema(UserSchema):
    favorites_count: int = 0
    read_count: int = 0
    recently_read_count: int = 0


class UserSchemaPaginated(CamelSerializerModel):
    results: list[UserDetailSchema]
    total_count: int
    current_page: int
    max_pages: int
    per_page: int
