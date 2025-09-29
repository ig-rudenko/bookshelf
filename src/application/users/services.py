from src.domain.auth.services import TokenService
from src.domain.common.unit_of_work import UnitOfWork
from .dto import UserDTO


async def get_user_by_token(token: str, *, token_service: TokenService, uow: UnitOfWork) -> UserDTO:
    user_id: int = await token_service.get_user_id(token)
    async with uow:
        user = await uow.users.get_by_id(user_id)
    return UserDTO(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        date_join=user.date_join,
    )
