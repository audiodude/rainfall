"""Add mastodon token, google id is no longer required

Revision ID: 3604b4c7a42c
Revises: f0e2ae637ca4
Create Date: 2024-01-19 11:31:50.825293

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3604b4c7a42c'
down_revision: Union[str, None] = 'f0e2ae637ca4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.create_table(
      'tmp_users', sa.Column('id', sa.Uuid(), nullable=False),
      sa.Column('google_id', sa.String(length=255), nullable=True),
      sa.Column('mastodon_netloc', sa.String(length=255), nullable=True),
      sa.Column('mastodon_auth_token', sa.String(length=255), nullable=True),
      sa.Column('name', sa.String(length=255), nullable=True),
      sa.Column('email', sa.String(length=1024), nullable=True),
      sa.Column('picture_url', sa.String(length=1024), nullable=True),
      sa.Column('is_welcomed', sa.Boolean(), nullable=False),
      sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('google_id'))

  op.execute('''
         INSERT INTO tmp_users
         SELECT id, google_id, NULL, NULL, name, email, picture_url, is_welcomed FROM users
  ''')

  op.drop_constraint(constraint_name='fk_sites_sites_users_id',
                     table_name='sites',
                     type_='foreignkey')
  op.drop_table('users')

  op.rename_table('tmp_users', 'users')


def downgrade() -> None:
  raise Exception("Irreversible migration")
