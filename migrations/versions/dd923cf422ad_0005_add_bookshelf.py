"""0005_add_bookshelf

Revision ID: dd923cf422ad
Revises: 4de0b4ab42e5
Create Date: 2024-09-10 05:31:48.842608

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'dd923cf422ad'
down_revision: Union[str, None] = '4de0b4ab42e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bookshelf',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk__bookshelf__user_id__users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__bookshelf')),
    sa.UniqueConstraint('name', name=op.f('uq__bookshelf__name'))
    )
    op.create_table('bookshelf_book_association',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('bookshelf_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], name=op.f('fk__bookshelf_book_association__book_id__books'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['bookshelf_id'], ['bookshelf.id'], name=op.f('fk__bookshelf_book_association__bookshelf_id__bookshelf'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk__bookshelf_book_association'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bookshelf_book_association')
    op.drop_table('bookshelf')
    # ### end Alembic commands ###
