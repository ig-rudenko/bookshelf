from pydantic import Field

from .base import CamelAliasModel


class TokenPair(CamelAliasModel):
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")


class AccessToken(CamelAliasModel):
    access_token: str = Field(..., alias="accessToken")


class RefreshToken(CamelAliasModel):
    refresh_token: str = Field(..., alias="refreshToken")
