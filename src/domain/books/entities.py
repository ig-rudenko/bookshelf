import contextlib
from dataclasses import dataclass, field
from typing import Self

from src.domain.common.exceptions import ValidationError


@dataclass(slots=True, kw_only=True)
class Tag:
    id: int
    name: str


@dataclass(slots=True, kw_only=True)
class Publisher:
    id: int
    name: str

    def __post_init__(self):
        if self.id < 0:
            raise ValidationError(f"Publisher id must be greater than 0, got {self.id}")


@dataclass(slots=True, kw_only=True)
class Book:
    id: int

    user_id: int
    publisher: Publisher

    title: str
    preview_image: str
    file: str
    authors: str
    description: str
    pages: int
    size: int
    year: int
    private: bool
    language: str

    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.id < 0:
            raise ValidationError(f"Book id must be greater than 0, got {self.id}")
        elif self.user_id <= 0:
            raise ValidationError(f"User id must be greater than 0, got {self.user_id}")
        if self.pages <= 0:
            raise ValidationError(f"Pages must be greater than 0, got {self.pages}")
        if self.size <= 0:
            raise ValidationError(f"Size must be greater than 0, got {self.size}")
        if self.year < 0:
            raise ValidationError(f"Year must be greater than 0, got {self.year}")

    @classmethod
    def create(
        cls,
        *,
        user_id: int,
        publisher: str,
        title: str,
        preview_image: str,
        file: str,
        authors: str,
        description: str,
        pages: int,
        size: int,
        year: int,
        private: bool,
        language: str,
        tags: list[str],
    ) -> Self:
        return cls(
            id=0,
            user_id=user_id,
            publisher=Publisher(
                id=0,
                name=publisher,
            ),
            title=title,
            preview_image=preview_image,
            file=file,
            authors=authors,
            description=description,
            pages=pages,
            size=size,
            year=year,
            private=private,
            language=language,
            tags=tags,
        )


@dataclass(slots=True, kw_only=True)
class BookFilter:
    """
    Attributes:
        viewer_id: Идентификатор пользователя, который запрашивает данные,
                    используется для ограничения доступа
        search: Поиск по названию, описанию
        title: Поиск по названию книги
        authors: Поиск по автору
        publisher: Поиск по издательству
        year: Поиск по году
        language: Поиск по языку
        pages_gt: Поиск книг с количеством страниц больше указанного
        pages_lt: Поиск книг с количеством страниц меньше указанного
        description: Поиск по описанию
        only_private: Отображать только приватные книги
        tags: Поиск по тегам
        page: Страница для отображения
        page_size: Количество книг на странице
        sorted_by: Поля для сортировки, по умолчанию: ("-year", "-id")
    """

    viewer_id: int | None = None
    search: str | None = None
    title: str | None = None
    authors: str | None = None
    publisher: str | None = None
    year: int | None = None
    language: str | None = None
    pages_gt: int | None = None
    pages_lt: int | None = None
    description: str | None = None
    only_private: bool | None = None
    tags: list[str] | None = None
    page: int = 1
    page_size: int = 25
    sorted_by: list[str] = field(default_factory=lambda: ["-year", "-id"])

    def remove_sorted_by_field(self, field_: str):
        with contextlib.suppress(ValueError):
            self.sorted_by.remove(field_)
            self.sorted_by.remove(f"-{field_}")


@dataclass(slots=True, kw_only=True)
class BookmarksQueryFilter:
    user_id: int
    page: int
    page_size: int
