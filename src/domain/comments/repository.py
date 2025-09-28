from abc import ABC, abstractmethod

from .entities import Comment


class CommentRepository(ABC):

    @abstractmethod
    def get(self, comment_id: int) -> Comment: ...

    @abstractmethod
    def get_filtered(self, *, user_id: int) -> list[Comment]: ...

    @abstractmethod
    def add(self, comment: Comment) -> Comment: ...

    @abstractmethod
    def update(self, comment: Comment) -> Comment: ...

    @abstractmethod
    def delete(self, comment_id: int) -> None: ...
