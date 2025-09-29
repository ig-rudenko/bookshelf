from .base import CamelSerializerModel, CamelAliasModel


class TokenPairSchema(CamelSerializerModel):
    access_token: str
    refresh_token: str


class AccessTokenSchema(CamelSerializerModel):
    access_token: str


class RefreshTokenSchema(CamelAliasModel):
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
