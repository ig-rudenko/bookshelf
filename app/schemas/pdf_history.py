from pydantic import BaseModel


class PDFHistorySchema(BaseModel):
    fingerprint: str
    sidebarView: int
    page: int
    zoom: str
    scrollLeft: int
    scrollTop: int
    rotation: int


class PDFHistoryFilesSchema(BaseModel):
    files: list[PDFHistorySchema]
