from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud.base import query_count
from ..models import User, Book, UserData
from ..schemas.books import BookWithReadPagesSchema, BooksWithReadPagesPaginatedSchema
from ..schemas.pdf_history import PDFHistoryFilesSchema
from ..services.paginator import paginate
from ..services.thumbnail import get_thumbnail


async def get_last_viewed_books(
    session: AsyncSession, user: User, paginator
) -> BooksWithReadPagesPaginatedSchema:
    query = (
        select(Book, UserData.pdf_history)
        .join(UserData)
        .where(UserData.user_id == user.id)
        .group_by(Book.id)
        .order_by(UserData.id.desc())
    )
    query = paginate(query, page=paginator["page"], per_page=paginator["per_page"])

    result = await session.execute(query)
    result.unique()
    count = await query_count(query, session)

    books_schemas = []
    for book, pdf_history in result.all():  # type: Book, str
        try:
            history = PDFHistoryFilesSchema.model_validate_json(pdf_history)
        except ValueError as e:
            print(e)
        else:
            if history.files:
                schema = BookWithReadPagesSchema.model_validate(book)
                schema.read_pages = history.files[-1].page
                schema.preview_image = get_thumbnail(book.preview_image, "medium")
                books_schemas.append(schema)

    return BooksWithReadPagesPaginatedSchema(
        books=books_schemas,
        total_count=count,
        current_page=paginator["page"],
        max_pages=count // paginator["per_page"] or 1,
        per_page=paginator["per_page"],
    )
