from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.base import CamelAliasModel, CamelSerializerModel


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


class CreatePdfJSHistorySchema(CamelAliasModel):
    pdf_history: str = Field(..., max_length=4096)


class PdfJSHistorySchema(CamelSerializerModel):
    id: int
    pdf_history: str
    pdf_history_updated_at: datetime | None
