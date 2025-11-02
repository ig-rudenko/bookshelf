from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import func, over, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.comments.entities import Comment, CommentFilter
from src.domain.comments.repository import CommentRepository
from src.infrastructure.db.exception_handler import wrap_sqlalchemy_exception
from src.infrastructure.db.models import CommentModel, UserModel


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
        query = (
            select(
                CommentModel.id,
                CommentModel.user_id,
                CommentModel.book_id,
                CommentModel.text,
                CommentModel.created_at,
                UserModel.username,
                over(func.count()).label("total_count"),
            )
            .join(UserModel)
            .group_by(CommentModel.id, UserModel.username)
            .order_by(CommentModel.created_at.desc())
            .limit(filter_.page_size)
            .offset(offset)
        )

        if filter_.book_id:
            query = query.where(CommentModel.book_id == filter_.book_id)
        if filter_.user_id:
            query = query.where(CommentModel.user_id == filter_.user_id)
        if filter_.search:
            query = query.where(CommentModel.text.like(f"%{filter_.search}%"))

        comments = []
        total = 0
        with wrap_sqlalchemy_exception(self._repo.dialect):
            result = await self.session.execute(query)
            result.unique()
            for i, row in enumerate(result):
                comments.append(
                    Comment(
                        id=row.id,
                        book_id=row.book_id,
                        user_id=row.user_id,
                        username=row.username,
                        text=row.text,
                        created_at=row.created_at,
                    )
                )
                if i == 0:
                    total = row.total_count

        return comments, total

    async def add(self, comment: Comment) -> Comment:
        model = self._to_model(comment)
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.add(model)
        return self._to_domain(model)

    async def update(self, comment: Comment) -> Comment:
        model = self._to_model(comment)
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.update(model)
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
            username=model.user.username,
            text=model.text,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_model(domain: Comment) -> CommentModel:
        return CommentModel(
            id=domain.id if domain.id else None,
            book_id=domain.book_id,
            user_id=domain.user_id,
            text=domain.text,
            created_at=domain.created_at,
        )
