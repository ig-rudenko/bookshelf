from .base import CamelSerializerModel, CamelAliasModel


class TokenPair(CamelSerializerModel):
    access_token: str
    refresh_token: str


class AccessToken(CamelSerializerModel):
    access_token: str


class RefreshToken(CamelAliasModel):
    refresh_token: str


class ForgotPasswordSchema(CamelAliasModel):
    email: str
    recaptcha_token: str


class ForgotPasswordResponseSchema(CamelSerializerModel):
    success: bool
    detail: str


class ResetPasswordSchema(CamelAliasModel):
    token: str
    password1: str
    password2: str
