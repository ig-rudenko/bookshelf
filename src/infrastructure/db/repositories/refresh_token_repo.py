from datetime import UTC, datetime
from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import update

from src.domain.auth.entities import JWToken
from src.domain.auth.repository import RefreshTokenRepository
from src.domain.common.exceptions import ObjectNotFoundError
from src.infrastructure.db.exception_handler import wrap_sqlalchemy_exception
from src.infrastructure.db.models import RefreshTokenModel


class SQLRefreshTokenRepository(SQLAlchemyAsyncRepository[RefreshTokenModel]):
    model_type = RefreshTokenModel

    @property
    def dialect(self):
        return self._dialect.name


class SqlAlchemyRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, session):
        self.session = session
        self._repo = SQLRefreshTokenRepository(
            session=session, auto_commit=False, auto_refresh=True, wrap_exceptions=False
        )

    async def get_by_hash(self, token_hash: str) -> JWToken:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.get_one(RefreshTokenModel.token_hash == token_hash)
        return self._to_domain(model)

    async def add(self, token: JWToken) -> JWToken:
        model = self._to_model(token)
        with wrap_sqlalchemy_exception(self._repo.dialect):
            await self._repo.add(model)
        return token

    async def revoke(self, token_hash: str) -> None:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            token = await self._repo.get_one(RefreshTokenModel.token_hash == token_hash)
        if token.revoked:
            raise ObjectNotFoundError("Refresh token not found or already revoked")
        else:
            token.revoked = True
            await self._repo.update(token, attribute_names=["revoked"])

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            stmt = update(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id).values(revoked=True)
            await self.session.execute(stmt)

    @staticmethod
    def _to_domain(model: RefreshTokenModel) -> JWToken:
        return JWToken(
            id=model.id,
            token_hash=model.token_hash,
            user_id=model.user_id,
            issued_at=datetime.fromtimestamp(model.issued_at, UTC),
            expire_at=model.expire_at,
            revoked=model.revoked,
            token="",
        )

    @staticmethod
    def _to_model(domain: JWToken) -> RefreshTokenModel:
        return RefreshTokenModel(
            id=domain.id if domain.id else None,
            token_hash=domain.token_hash,
            user_id=domain.user_id,
            issued_at=int(domain.issued_at.timestamp()),
            expire_at=domain.expire_at,
            revoked=domain.revoked,
        )
