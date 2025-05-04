"""add_metadata_fields_to_file

Revision ID: e932aec0076e
Revises: 20a525107a88
Create Date: 2025-04-27 15:20:17.642151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e932aec0076e'
down_revision: Union[str, None] = '20a525107a88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  # Add new metadata columns to files table
  op.add_column('files', sa.Column('title', sa.String(1024), nullable=True))
  op.add_column('files', sa.Column('artist', sa.String(1024), nullable=True))
  op.add_column('files', sa.Column('year', sa.String(4), nullable=True))
  op.add_column('files', sa.Column('track_number', sa.String(10),
                                   nullable=True))
  op.add_column('files', sa.Column('genre', sa.String(1024), nullable=True))


def downgrade() -> None:
  # Remove metadata columns from files table
  op.drop_column('files', 'title')
  op.drop_column('files', 'artist')
  op.drop_column('files', 'year')
  op.drop_column('files', 'track_number')
  op.drop_column('files', 'genre')
