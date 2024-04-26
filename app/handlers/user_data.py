from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..orm.session_manager import get_session
from ..schemas.pdf_history import CreatePdfJSHistorySchema, PdfJSHistorySchema
from ..services.auth import get_current_user
from ..services.pdf_history import get_pdf_history_data, set_pdf_history_data

router = APIRouter(prefix="/user-data", tags=["user-data"])


@router.get("/book/{book_id}/pdf-history", response_model=PdfJSHistorySchema)
async def get_pdf_history_view(
    book_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Возвращает место на котором остановился просмотр книги."""
    return await get_pdf_history_data(session, current_user.id, book_id)


@router.put("/book/{book_id}/pdf-history", response_model=PdfJSHistorySchema)
async def set_pdf_history_view(
    book_id: int,
    data: CreatePdfJSHistorySchema,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session, use_cache=True),
):
    """Сохраняет данные о просмотре книги."""
    return await set_pdf_history_data(session, current_user.id, book_id, data)
