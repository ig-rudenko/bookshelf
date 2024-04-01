from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    username: str = Field(..., min_length=2, max_length=150)
    email: EmailStr = Field(..., max_length=254)
    first_name: str | None = Field(None, max_length=150)
    last_name: str | None = Field(None, max_length=150)


class UserCredentials(BaseModel):
    username: str = Field(..., max_length=150)
    password: str = Field(..., max_length=128)


class UserCreate(User):
    password: str = Field(..., min_length=8, max_length=50)
