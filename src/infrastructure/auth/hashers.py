from abc import ABC, abstractmethod

import bcrypt


class PasswordHasherProtocol(ABC):
    @abstractmethod
    def hash(self, password: str) -> str: ...
    @abstractmethod
    def verify(self, password: str, hash_: str) -> bool: ...


class BcryptPasswordHasher(PasswordHasherProtocol):

    def hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify(self, password: str, hash_: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode("utf-8"), hash_.encode("utf-8"))
