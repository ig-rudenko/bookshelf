"""0004_add_reset_passwd_email_datetime

Revision ID: 4de0b4ab42e5
Revises: 3c951d1adafe
Create Date: 2024-05-01 17:51:05.978039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4de0b4ab42e5'
down_revision: Union[str, None] = '3c951d1adafe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('reset_passwd_email_datetime', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'reset_passwd_email_datetime')
    # ### end Alembic commands ###
