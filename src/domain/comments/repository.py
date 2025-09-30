from abc import ABC, abstractmethod

from .entities import Comment, CommentFilter


class CommentRepository(ABC):

    @abstractmethod
    async def get(self, comment_id: int) -> Comment: ...

    @abstractmethod
    async def get_filtered(self, filter_: CommentFilter) -> tuple[list[Comment], int]: ...

    @abstractmethod
    async def add(self, comment: Comment) -> Comment: ...

    @abstractmethod
    async def update(self, comment: Comment) -> Comment: ...

    @abstractmethod
    async def delete(self, comment_id: int) -> None: ...
