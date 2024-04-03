from .base import BaseConfigModel


class TokenPair(BaseConfigModel):
    access_token: str
    refresh_token: str


class AccessToken(BaseConfigModel):
    access_token: str


class RefreshToken(BaseConfigModel):
    refresh_token: str
