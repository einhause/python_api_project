"""Add Content Column to Posts table

Revision ID: 95ba5097d099
Revises: 6040e09fa60b
Create Date: 2023-09-09 19:27:41.907379

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95ba5097d099'
down_revision: Union[str, None] = '6040e09fa60b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column("content", sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
