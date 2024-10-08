"""Add description to release

Revision ID: 8b02ba45053c
Revises: 5a0902890ee4
Create Date: 2024-01-26 12:56:22.793346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b02ba45053c'
down_revision: Union[str, None] = '5a0902890ee4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('releases', sa.Column('description', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('releases', 'description')
    # ### end Alembic commands ###
