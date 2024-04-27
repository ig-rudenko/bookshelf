from passlib.context import CryptContext

__pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def encrypt_password(password: str) -> str:
    return __pwd_context.hash(password)


def validate_password(plain_password: str, hashed_password: str) -> bool:
    return __pwd_context.verify(plain_password, hashed_password)
