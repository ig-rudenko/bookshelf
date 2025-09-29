from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class RegisterUserCommand:
    username: str
    email: str
    password: str
    first_name: str = ""
    last_name: str = ""


@dataclass(slots=True, kw_only=True)
class LoginUserCommand:
    username: str
    password: str


@dataclass(slots=True, kw_only=True)
class ForgotPasswordCommand:
    email: str


@dataclass(slots=True, kw_only=True)
class ResetPasswordCommand:
    user_id: int
    password: str
