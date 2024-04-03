from datetime import datetime

from pydantic import Field, EmailStr

from .base import BaseConfigModel


class User(BaseConfigModel):
    username: str = Field(..., min_length=2, max_length=150)
    email: EmailStr = Field(..., max_length=254)
    first_name: str | None = Field(None, max_length=150)
    last_name: str | None = Field(None, max_length=150)
    is_superuser: bool
    is_staff: bool
    is_active: bool
    date_join: datetime


class UserCredentials(BaseConfigModel):
    username: str = Field(..., max_length=150)
    password: str = Field(..., max_length=128)


class UserCreate(BaseConfigModel):
    username: str = Field(..., min_length=2, max_length=150)
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=50)
