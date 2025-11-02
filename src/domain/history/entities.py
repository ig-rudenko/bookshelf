from dataclasses import dataclass
from datetime import datetime
from typing import Self

from pydantic import BaseModel


class BookStopReadPosition(BaseModel):
    fingerprint: str
    sidebarView: int
    page: int
    zoom: str | int
    scrollLeft: int
    scrollTop: int
    rotation: int


class BookReadFilesHistory(BaseModel):
    files: list[BookStopReadPosition]


@dataclass(slots=True, kw_only=True)
class BookReadHistory:
    id: int
    user_id: int
    book_id: int
    updated_at: datetime
    history: BookReadFilesHistory

    @classmethod
    def create(cls, *, id_: int, user_id: int, book_id: int, history: str, updated_at: datetime) -> Self:
        return cls(
            id=id_,
            user_id=user_id,
            book_id=book_id,
            updated_at=updated_at,
            history=BookReadFilesHistory.model_validate_json(history),
        )


@dataclass(slots=True, kw_only=True)
class BookReadHistoryFilter:
    user_id: int | None
    page: int
    page_size: int
