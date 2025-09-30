from pydantic import ValidationError as PydanticValidationError

from src.domain.common.unit_of_work import UnitOfWork
from src.domain.history.entities import BookReadFilesHistory

from ...domain.common.exceptions import ValidationError
from .commands import SetReadBookHistory
from .dto import BookReadHistoryDTO


class HistoryQueryHandler:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def handle_get(self, user_id: int, book_id: int) -> BookReadHistoryDTO:
        async with self.uow:
            history = await self.uow.book_read_history.get_last_for_user(book_id=book_id, user_id=user_id)
        return BookReadHistoryDTO(
            id=history.id,
            history=history.history.model_dump_json(),
            updated_at=history.updated_at,
        )


class HistoryCommandHandler:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def handle_update(self, cmd: SetReadBookHistory) -> BookReadHistoryDTO:
        try:
            history_data = BookReadFilesHistory.model_validate_json(cmd.history)
        except PydanticValidationError as exc:
            raise ValidationError(exc.errors()) from exc
        async with self.uow:
            read_history = await self.uow.book_read_history.get_last_for_user(
                user_id=cmd.user_id, book_id=cmd.book_id
            )
            read_history.history = history_data
            read_history = await self.uow.book_read_history.update(read_history)
        return BookReadHistoryDTO(
            id=read_history.id,
            history=read_history.history.model_dump_json(),
            updated_at=read_history.updated_at,
        )
