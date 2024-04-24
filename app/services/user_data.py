from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserData
from app.schemas.user_data import PdfJSHistorySchema, CreatePdfJSHistorySchema


async def get_pdf_history_data(session: AsyncSession, user_id: int, book_id: int) -> PdfJSHistorySchema:
    try:
        user_data = await UserData.get(session, user_id=user_id, book_id=book_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Пользовательские данные не существуют")
    return PdfJSHistorySchema.model_validate(user_data)


async def set_pdf_history_data(
    session: AsyncSession, user_id: int, book_id: int, data: CreatePdfJSHistorySchema
) -> PdfJSHistorySchema:
    try:
        user_data = await UserData.get(session, user_id=user_id, book_id=book_id)
    except NoResultFound:
        user_data = await UserData.create(
            session, pdf_history=data.pdf_history, user_id=user_id, book_id=book_id
        )
    else:
        user_data.pdf_history = data.pdf_history
        await user_data.save(session)

    return PdfJSHistorySchema.model_validate(user_data)
