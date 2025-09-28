import re
from contextlib import contextmanager
from typing import Generator

from advanced_alchemy import exceptions as advanced_alchemy_exceptions
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.exc import InvalidRequestError as SQLAlchemyInvalidRequestError
from sqlalchemy.exc import MultipleResultsFound, SQLAlchemyError, StatementError

from src.domain.common.exceptions import (
    MultipleResultsFoundError,
    ObjectNotFoundError,
    RepositoryError,
    UniqueError,
)


@contextmanager
def wrap_sqlalchemy_exception(  # noqa: C901, PLR0915
    dialect_name: str | None = None,
) -> Generator[None, None, None]:
    """Do something within context to raise a ``RepositoryError`` chained
    from an original ``SQLAlchemyError``.

        >>> try:
        ...     with wrap_sqlalchemy_exception():
        ...         raise SQLAlchemyError("Original Exception")
        ... except RepositoryError as exc:
        ...     print(f"caught repository exception from {type(exc.__context__)}")
        caught repository exception from <class 'sqlalchemy.exc.SQLAlchemyError'>

    Args:
        dialect_name: The name of the dialect to use for the exception.

    Raises:
        ObjectNotFoundError: Raised when no rows matched the specified data.
        MultipleResultsFoundError: Raised when multiple rows matched the specified data.
        RepositoryError: Raised for other SQLAlchemy errors.
    """
    try:
        yield

    except advanced_alchemy_exceptions.NotFoundError as exc:
        raise ObjectNotFoundError("Object not found") from exc
    except MultipleResultsFound as exc:
        raise MultipleResultsFoundError("Multiple objects found") from exc
    except SQLAlchemyIntegrityError as exc:
        if dialect_name is not None:
            keys_to_regex: dict[str, list[re.Pattern[str]]] = {
                "duplicate_key": advanced_alchemy_exceptions.DUPLICATE_KEY_REGEXES.get(dialect_name, []),
                "check_constraint": advanced_alchemy_exceptions.CHECK_CONSTRAINT_REGEXES.get(
                    dialect_name, []
                ),
                "foreign_key": advanced_alchemy_exceptions.FOREIGN_KEY_REGEXES.get(dialect_name, []),
            }
            detail = " - ".join(str(exc_arg) for exc_arg in exc.orig.args) if exc.orig.args else ""  # type: ignore[union-attr] # pyright: ignore[reportArgumentType,reportOptionalMemberAccess]
            for key, regexes in keys_to_regex.items():
                for regex in regexes:
                    if match := regex.search(detail):
                        matched = match.groupdict()
                        if key == "duplicate_key":
                            verbose_key = matched.get("key", "") or matched.get("columns", "") or "id"
                            full_part, _, field = verbose_key.partition(".")
                            raise UniqueError(
                                f"Object with same {field or full_part} already exists",
                                field=field or full_part,
                            ) from exc

        raise RepositoryError("Integrity error") from exc

    except SQLAlchemyInvalidRequestError as exc:
        raise RepositoryError("An invalid request was made.") from exc
    except StatementError as exc:
        raise RepositoryError("There was an issue processing the statement") from exc
    except SQLAlchemyError as exc:
        raise RepositoryError("An error occurred during processing") from exc
    except AttributeError as exc:
        raise RepositoryError(f"An attribute error occurred during processing: {exc}") from exc
