"""create integrations table

Revision ID: 47f4cef012e7
Revises: 3eb712c93cdb
Create Date: 2024-11-08 19:42:41.755820

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '47f4cef012e7'
down_revision: Union[str, None] = '3eb712c93cdb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.create_table(
      'integrations', sa.Column('id', sa.Uuid(), nullable=False),
      sa.Column('user_id', sa.Uuid(), nullable=False),
      sa.Column('netlify_access_token', sa.String(length=255), nullable=True),
      sa.ForeignKeyConstraint(
          ['user_id'],
          ['users.id'],
      ), sa.PrimaryKeyConstraint('id'))


def downgrade() -> None:
  op.drop_table('integrations')
