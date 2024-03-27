from pydantic import BaseModel, Field


class TokenPair(BaseModel):
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")


class AccessToken(BaseModel):
    access_token: str = Field(..., alias="accessToken")


class RefreshToken(BaseModel):
    refresh_token: str = Field(..., alias="refreshToken")
