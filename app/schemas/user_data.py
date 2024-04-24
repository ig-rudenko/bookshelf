from pydantic import Field

from .base import CamelSerializerModel, CamelAliasModel


class CreatePdfJSHistorySchema(CamelAliasModel):
    pdf_history: str = Field(..., max_length=256)


class PdfJSHistorySchema(CamelSerializerModel):
    id: int
    pdf_history: str
