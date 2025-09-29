from advanced_alchemy.filters import LimitOffset, OrderBy
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.common.exceptions import ObjectNotFoundError
from src.domain.history.entities import BookReadHistory, BookReadHistoryFilter
from src.domain.history.repository import BookReadHistoryRepository
from src.infrastructure.db.exception_handler import wrap_sqlalchemy_exception
from src.infrastructure.db.models import BookHistoryModel


class SQLHistoryRepository(SQLAlchemyAsyncRepository[BookHistoryModel]):
    model_type = BookHistoryModel

    @property
    def dialect(self):
        return self._dialect.name


class SqlAlchemyBookReadHistoryRepositoryRepository(BookReadHistoryRepository):

    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = SQLHistoryRepository(
            session=session, auto_commit=False, auto_refresh=True, wrap_exceptions=False
        )

    async def get_last_for_user(self, book_id: int, user_id: int) -> BookReadHistory:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            results = self._repo.list(
                LimitOffset(limit=1, offset=0),
                OrderBy("id", "desc"),
                BookHistoryModel.book_id == book_id,
                BookHistoryModel.user_id == user_id,
            )
            if not results or not results[0]:
                raise ObjectNotFoundError(f"No history found for book_id `{book_id}` and user_id `{user_id}`")
        return self._to_domain(results[0])

    async def get_filtered(self, filter_: BookReadHistoryFilter) -> tuple[list[BookReadHistory], int]:
        offset = (filter_.page - 1) * filter_.page_size
        filters = [
            LimitOffset(limit=filter_.page_size, offset=offset),
            OrderBy("pdf_history_updated_at", "desc"),
        ]
        if filter_.user_id:
            filters.append(
                BookHistoryModel.user_id == filter_.user_id,
            )

        with wrap_sqlalchemy_exception(self._repo.dialect):
            results, count = self._repo.list_and_count(*filters)
            return results, count

    async def add(self, book_history: BookReadHistory) -> BookReadHistory:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            await self._repo.add(self._to_model(book_history))
            return book_history

    async def update(self, book_history: BookReadHistory) -> BookReadHistory:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            await self._repo.update(
                self._to_model(book_history),
                attribute_names=[
                    "book_id",
                    "user_id",
                    "pdf_history",
                    "pdf_history_updated_at",
                ],
            )
            return book_history

    async def delete_for_user(self, user_id: int, book_id: int) -> None:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            query = delete(BookHistoryModel).where(
                BookHistoryModel.user_id == user_id,
                BookHistoryModel.book_id == book_id,
            )
            await self.session.execute(query)

    async def delete_for_book(self, book_id: int) -> None:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            query = delete(BookHistoryModel).where(
                BookHistoryModel.book_id == book_id,
            )
            await self.session.execute(query)

    @staticmethod
    def _to_model(book_history: BookReadHistory) -> BookHistoryModel:
        return BookHistoryModel(
            id=book_history.id if book_history.id else None,
            book_id=book_history.book_id,
            user_id=book_history.user_id,
            pdf_history=book_history.history.model_dump_json(),
            pdf_history_updated_at=book_history.updated_at,
        )

    @staticmethod
    def _to_domain(model: BookHistoryModel) -> BookReadHistory:
        return BookReadHistory.create(
            id_=model.id,
            book_id=model.book_id,
            user_id=model.user_id,
            updated_at=model.pdf_history_updated_at,
            history=model.pdf_history,
        )
