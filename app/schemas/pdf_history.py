from pydantic import BaseModel


class PDFHistorySchema(BaseModel):
    fingerprint: str
    sidebarView: int
    page: int
    zoom: str | int
    scrollLeft: int
    scrollTop: int
    rotation: int


class PDFHistoryFilesSchema(BaseModel):
    files: list[PDFHistorySchema]
