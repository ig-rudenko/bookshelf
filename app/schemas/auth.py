from .base import CamelSerializerModel, CamelAliasModel


class TokenPair(CamelSerializerModel):
    access_token: str
    refresh_token: str


class AccessToken(CamelSerializerModel):
    access_token: str


class RefreshToken(CamelAliasModel):
    refresh_token: str
