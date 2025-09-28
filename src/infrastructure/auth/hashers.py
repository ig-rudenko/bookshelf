from abc import ABC, abstractmethod

from passlib.context import CryptContext


class PasswordHasherProtocol(ABC):
    @abstractmethod
    def hash(self, password: str) -> str: ...
    @abstractmethod
    def verify(self, password: str, hash_: str) -> bool: ...


class BcryptPasswordHasher(PasswordHasherProtocol):
    def __init__(self):
        self.ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self.ctx.hash(password)

    def verify(self, password: str, hash_: str) -> bool:
        return self.ctx.verify(password, hash_)
