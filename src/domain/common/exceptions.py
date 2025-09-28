class DomainError(Exception):
    """Базовое исключение доменной логики."""


class ValidationError(DomainError): ...


class NotFoundError(DomainError): ...


class UnauthorizedError(DomainError): ...


class PermissionDeniedError(DomainError): ...


class RepositoryError(Exception):
    """Базовое исключение репозитория."""


class UniqueError(RepositoryError):

    def __init__(self, message, *, field):
        super().__init__(message)
        self.message = message
        self.field = field


class ObjectNotFoundError(RepositoryError):
    """Объект не найден в репозитории."""


class MultipleResultsFoundError(RepositoryError):
    """Если в репозитории найдено несколько объектов."""


class AuthorizationError(Exception):
    pass


class RefreshTokenRevokedError(AuthorizationError):
    pass


class InvalidTokenError(AuthorizationError):
    pass
