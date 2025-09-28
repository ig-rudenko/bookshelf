from pydantic import BaseModel


class BookStopReadPosition(BaseModel):
    fingerprint: str
    sidebarView: int
    page: int
    zoom: str | int
    scrollLeft: int
    scrollTop: int
    rotation: int


class BookReadHistory(BaseModel):
    files: list[BookStopReadPosition]
