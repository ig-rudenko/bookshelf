from fastapi import APIRouter, Depends, status

from src.application.comments.commands import CreateCommentCommand, UpdateCommentCommand
from src.application.comments.handler import CommentsCommandHandler, CommentsQueryHandler
from src.application.comments.queries import CommentsListQuery
from src.application.users.dto import UserDTO

from ..auth import get_current_user, get_user_or_none
from ..dependencies import get_comment_command_handler, get_comment_query_handler
from ..schemas.comments import CommentCreateUpdateSchema, CommentsPaginateSchema, CommentUserSchema
from .queries import PaginatorQuery, paginator_query

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/book/{book_id}", response_model=CommentsPaginateSchema)
async def get_book_comments_view(
    book_id: int,
    query_params: PaginatorQuery = Depends(paginator_query),
    user: UserDTO | None = Depends(get_user_or_none),
    handler: CommentsQueryHandler = Depends(get_comment_query_handler),
):
    """Возвращает список комментариев к книге"""
    comments, total = await handler.handle_comments_list(
        CommentsListQuery(
            page=query_params.page,
            page_size=query_params.per_page,
            book_id=book_id,
            user=user,
        )
    )

    return CommentsPaginateSchema(
        comments=CommentUserSchema.from_dto_many(comments),
        total_count=total,
        current_page=query_params.page,
        per_page=query_params.per_page,
        max_pages=(
            total // query_params.per_page
            if total % query_params.per_page
            else total // query_params.per_page + 1
        ),
    )


@router.post("/book/{book_id}", status_code=status.HTTP_201_CREATED, response_model=CommentUserSchema)
async def create_book_comment_view(
    book_id: int,
    comment_data: CommentCreateUpdateSchema,
    user: UserDTO = Depends(get_current_user),
    handler: CommentsCommandHandler = Depends(get_comment_command_handler),
):
    """Создание комментария к книге"""
    comment = await handler.handle_comment_create(
        CreateCommentCommand(
            user=user,
            book_id=book_id,
            text=comment_data.text,
        )
    )
    return CommentUserSchema.from_dto(comment)


@router.put("/{comment_id}", response_model=CommentUserSchema)
async def update_comment_view(
    comment_id: int,
    comment_data: CommentCreateUpdateSchema,
    user: UserDTO = Depends(get_current_user),
    handler: CommentsCommandHandler = Depends(get_comment_command_handler),
):
    """Редактирование комментария"""
    comment = await handler.handle_comment_update(
        UpdateCommentCommand(
            user=user,
            comment_id=comment_id,
            text=comment_data.text,
        )
    )
    return CommentUserSchema.from_dto(comment)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_view(
    comment_id: int,
    user: UserDTO = Depends(get_current_user),
    handler: CommentsCommandHandler = Depends(get_comment_command_handler),
) -> None:
    """Удаление комментария"""
    await handler.handle_comment_delete(comment_id, user.id)
