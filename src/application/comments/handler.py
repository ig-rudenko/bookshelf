from src.domain.common.unit_of_work import UnitOfWork
from .commands import CreateCommentCommand, UpdateCommentCommand
from .dto import CommentDTO
from .queries import CommentsListQuery
from ...domain.comments.entities import Comment, CommentFilter
from ...domain.common.exceptions import ObjectNotFoundError


class CommentsQueryHandler:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def handle_comments_list(self, query: CommentsListQuery) -> tuple[list[CommentDTO], int]:
        async with self.uow:
            book = await self.uow.books.get_by_id(query.book_id)
            if book.private and (
                not query.user or query.user.id != book.user_id or not query.user.is_superuser
            ):
                raise ObjectNotFoundError("Object not found")
            comments, count = await self.uow.comments.get_filtered(
                CommentFilter(
                    book_id=book.id,
                    page=query.page,
                    page_size=query.page_size,
                )
            )

        result = [
            CommentDTO(
                id=comment.id,
                text=comment.text,
                user_id=comment.user_id,
                username=comment.username,
                created_at=comment.created_at,
            )
            for comment in comments
        ]

        return result, count


class CommentsCommandHandler:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def handle_comment_create(self, cmd: CreateCommentCommand) -> CommentDTO:
        async with self.uow:
            book = await self.uow.books.get_by_id(cmd.book_id)
            if book.private and (cmd.user.id != book.user_id or not cmd.user.is_superuser):
                raise ObjectNotFoundError("Object not found")

            comment = await self.uow.comments.add(
                Comment.create(
                    user_id=cmd.user.id,
                    book_id=cmd.book_id,
                    text=cmd.text,
                )
            )
            return CommentDTO.from_domain(comment)

    async def handle_comment_update(self, cmd: UpdateCommentCommand) -> CommentDTO:
        async with self.uow:
            comment = await self.uow.comments.get(cmd.comment_id)
            if comment.user_id != cmd.user.id and not cmd.user.is_superuser:
                raise ObjectNotFoundError("Object not found")
            comment.text = cmd.text
            comment = await self.uow.comments.update(comment)

        return CommentDTO.from_domain(comment)

    async def handle_comment_delete(self, comment_id: int, user_id: int) -> None:
        async with self.uow:
            comment = await self.uow.comments.get(comment_id)
            if comment.user_id != user_id:
                raise ObjectNotFoundError("Object not found")
            await self.uow.comments.delete(comment_id)
