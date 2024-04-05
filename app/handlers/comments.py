from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.orm.session_manager import get_session
from app.schemas.comments import CommentCreateUpdateSchema, CommentSchema, CommentUserSchema
from app.services.auth import get_user_or_none, get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/book/{book_id}", response_model=list[CommentUserSchema])
async def get_book_comments_view(
    book_id: int,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_user_or_none),
):
    pass


@router.post("/book/{book_id}", status_code=status.HTTP_201_CREATED, response_model=CommentSchema)
async def create_book_comment_view(
    book_id: int,
    comment_data: CommentCreateUpdateSchema,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_user_or_none),
):
    pass


@router.put("/{comment_id}", response_model=CommentSchema)
async def update_comment_view(
    book_id: int,
    comment_data: CommentCreateUpdateSchema,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    pass


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_view(
    book_id: int,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    pass
