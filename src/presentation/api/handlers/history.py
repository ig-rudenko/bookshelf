from fastapi import APIRouter, Depends

from src.application.history.commands import SetReadBookHistory
from src.application.history.handlers import HistoryCommandHandler, HistoryQueryHandler
from src.application.users.dto import UserDTO

from ..auth import get_current_user
from ..dependencies import get_history_command_handler, get_history_query_handler
from ..schemas.history import CreatePdfJSHistorySchema, PdfJSHistorySchema

router = APIRouter(prefix="/user-data", tags=["user-data"])


@router.get("/book/{book_id}/pdf-history", response_model=PdfJSHistorySchema)
async def get_pdf_history_view(
    book_id: int,
    current_user: UserDTO = Depends(get_current_user),
    handler: HistoryQueryHandler = Depends(get_history_query_handler),
):
    """Возвращает место на котором остановился просмотр книги."""
    history = await handler.handle_get(book_id=book_id, user_id=current_user.id)
    return PdfJSHistorySchema(
        id=history.id,
        pdf_history=history.history,
        pdf_history_updated_at=history.updated_at,
    )


@router.put("/book/{book_id}/pdf-history", response_model=PdfJSHistorySchema)
async def set_pdf_history_view(
    book_id: int,
    data: CreatePdfJSHistorySchema,
    current_user: UserDTO = Depends(get_current_user),
    handler: HistoryCommandHandler = Depends(get_history_command_handler),
):
    """Сохраняет данные о просмотре книги."""
    history = await handler.handle_update(
        SetReadBookHistory(
            book_id=book_id,
            user_id=current_user.id,
            history=data.pdf_history,
        )
    )
    return PdfJSHistorySchema(
        id=history.id,
        pdf_history=history.history,
        pdf_history_updated_at=history.updated_at,
    )
