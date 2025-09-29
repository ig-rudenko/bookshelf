from uuid import UUID

from advanced_alchemy.filters import LimitOffset
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.users.entities import User
from src.domain.users.repository import UserRepository
from src.infrastructure.db.exception_handler import wrap_sqlalchemy_exception
from src.infrastructure.db.models import UserModel


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
