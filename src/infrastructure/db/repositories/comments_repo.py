from advanced_alchemy.filters import LimitOffset
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.comments.entities import Comment, CommentFilter
from src.domain.comments.repository import CommentRepository
from src.infrastructure.db.exception_handler import wrap_sqlalchemy_exception
from src.infrastructure.db.models import CommentModel


class SQLCommentRepository(SQLAlchemyAsyncRepository[CommentModel]):
    model_type = CommentModel

    @property
    def dialect(self):
        return self._dialect.name


class SqlAlchemyCommentRepository(CommentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = SQLCommentRepository(
            session=session, auto_commit=False, auto_refresh=True, wrap_exceptions=False
        )

    async def get(self, comment_id: int) -> Comment:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.get(comment_id)
        return self._to_domain(model)

    async def get_filtered(self, filter_: CommentFilter) -> tuple[list[Comment], int]:
        offset = (filter_.page - 1) * filter_.page_size
        filters = [
            LimitOffset(limit=filter_.page_size, offset=offset),
        ]
        if filter_.book_id:
            filters.append(CommentModel.book_id == filter_.book_id)
        if filter_.user_id:
            filters.append(CommentModel.user_id == filter_.user_id)
        if filter_.search:
            filters.append(CommentModel.text.like(f"%{filter_.search}%"))

        with wrap_sqlalchemy_exception(self._repo.dialect):
            result, total = await self._repo.list_and_count(*filters)

        return [self._to_domain(model) for model in result], total

    async def add(self, comment: Comment) -> Comment:
        model = self._to_model(comment)
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.add(model)
        return self._to_domain(model)

    async def update(self, comment: Comment) -> Comment:
        model = self._to_model(comment)
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.update(model, attribute_names=["text", "user_id", "book_id"])
        return self._to_domain(model)

    async def delete(self, comment_id: int) -> None:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            await self._repo.delete(comment_id)

    @staticmethod
    def _to_domain(model: CommentModel) -> Comment:
        return Comment(
            id=model.id,
            book_id=model.book_id,
            user_id=model.user_id,
            text=model.text,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(domain: Comment) -> CommentModel:
        return CommentModel(
            id=domain.id,
            book_id=domain.book_id,
            user_id=domain.user_id,
            text=domain.text,
            created_at=domain.created_at,
        )
