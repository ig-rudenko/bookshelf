from uuid import UUID

from advanced_alchemy.filters import LimitOffset
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import func, over, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.users.entities import User, UserDetail, UserFilter
from src.domain.users.repository import UserRepository
from src.infrastructure.db.exception_handler import wrap_sqlalchemy_exception
from src.infrastructure.db.models import BookHistoryModel, FavoriteBookModel, ReadBookModel, UserModel


class SQLUserRepository(SQLAlchemyAsyncRepository[UserModel]):
    model_type = UserModel

    @property
    def dialect(self):
        return self._dialect.name


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = SQLUserRepository(
            session=session, auto_commit=False, auto_refresh=True, wrap_exceptions=False
        )

    async def get_by_id(self, user_id: UUID) -> User:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.get(user_id)
        return self._to_domain(model)

    async def get_by_username(self, username: str) -> User:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.get_one(UserModel.username == username)
        return self._to_domain(model)

    async def get_by_email(self, email: str) -> User:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.get_one(UserModel.email == email)
        return self._to_domain(model)

    async def get_filtered(self, page: int, page_size: int) -> tuple[list[User], int]:
        offset = (page - 1) * page_size
        with wrap_sqlalchemy_exception(self._repo.dialect):
            results, total = await self._repo.list_and_count(LimitOffset(offset=offset, limit=page_size))
        return [self._to_domain(r) for r in results], total

    async def add(self, user: User) -> User:
        model = self._to_model(user)
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.add(model)
        return self._to_domain(model)

    async def update(self, user: User) -> User:
        model = self._to_model(user)
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.update(
                model,
                attribute_names=[
                    "username",
                    "email",
                    "password",
                    "first_name",
                    "last_name",
                    "is_superuser",
                    "is_active",
                    "is_staff",
                    "last_login",
                    "reset_passwd_email_datetime",
                ],
            )
        return self._to_domain(model)

    async def delete(self, user_id: UUID) -> None:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            await self._repo.delete(user_id)

    async def get_filtered_detail(self, filter_: UserFilter) -> tuple[list[UserDetail], int]:
        query = (
            select(
                over(func.count()).label("count"),
                UserModel.id,
                UserModel.username,
                UserModel.first_name,
                UserModel.last_name,
                UserModel.email,
                UserModel.password,
                UserModel.last_login,
                UserModel.is_superuser,
                UserModel.is_staff,
                UserModel.is_active,
                UserModel.date_join,
                UserModel.reset_passwd_email_datetime,
                func.count(func.distinct(FavoriteBookModel.book_id)).label("favorites_count"),
                func.count(func.distinct(ReadBookModel.book_id)).label("read_count"),
                func.count(func.distinct(BookHistoryModel.book_id)).label("recently_read_count"),
            )
            .outerjoin(FavoriteBookModel, UserModel.id == FavoriteBookModel.user_id)
            .outerjoin(ReadBookModel, UserModel.id == ReadBookModel.user_id)
            .outerjoin(BookHistoryModel, UserModel.id == BookHistoryModel.user_id)
            .group_by(UserModel.id)
        )
        query = query.offset((filter_.page - 1) * filter_.per_page).limit(filter_.per_page)

        if sort_by := filter_.sort_by:
            if sort_by == "favorites_count":
                query = query.order_by(func.count(FavoriteBookModel.book_id).desc())
            elif sort_by == "read_count":
                query = query.order_by(func.count(ReadBookModel.book_id).desc())
            elif sort_by == "recently_read_count":
                query = query.order_by(func.count(BookHistoryModel.book_id).desc())
            elif hasattr(UserModel, sort_by):
                if filter_.sort_order == "desc":
                    query = query.order_by(getattr(UserModel, sort_by).desc())
                else:
                    query = query.order_by(getattr(UserModel, sort_by).asc())

        result = await self.session.execute(query)

        total_count = 0
        users: list[UserDetail] = []

        for i, row in enumerate(result):
            users.append(
                UserDetail(
                    id=row.id,
                    username=row.username,
                    first_name=row.first_name,
                    last_name=row.last_name,
                    email=row.email,
                    password=row.password,
                    last_login=row.last_login,
                    is_superuser=row.is_superuser,
                    is_staff=row.is_staff,
                    is_active=row.is_active,
                    date_join=row.date_join,
                    reset_passwd_email_datetime=row.reset_passwd_email_datetime,
                    favorites_count=row.favorites_count,
                    read_count=row.read_count,
                    recently_read_count=row.recently_read_count,
                )
            )
            if i == 0:
                total_count = row.count

        return users, total_count

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            password=model.password,
            first_name=model.first_name,
            last_name=model.last_name,
            is_superuser=model.is_superuser,
            is_active=model.is_active,
            date_join=model.date_join,
            is_staff=model.is_staff,
            last_login=model.last_login,
            reset_passwd_email_datetime=model.reset_passwd_email_datetime,
        )

    @staticmethod
    def _to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id if user.id else None,
            username=user.username,
            password=user.password,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_superuser=user.is_superuser,
            is_active=user.is_active,
            date_join=user.date_join,
            is_staff=user.is_staff,
            last_login=user.last_login,
            reset_passwd_email_datetime=user.reset_passwd_email_datetime,
        )
