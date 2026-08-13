"""Backfill song metadata

Revision ID: backfill_song_metadata
Revises: 03e6e9292a46
Create Date: 2024-12-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from rainfall.models.file import File
from rainfall.db import db
import os
import mutagen
from rainfall.site import release_path, secure_filename

# revision identifiers, used by Alembic.
revision: str = 'backfill_song_metadata'
down_revision: Union[str, None] = '03e6e9292a46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  bind = op.get_context().bind
  session = Session(bind)
  data_dir = os.environ.get('DATA_DIR', 'data')

  for f in session.query(File).all():
    try:
      release = f.release
      if not release or not release.site:
        continue
      file_path = os.path.join(release_path(data_dir, release.site), secure_filename(f.filename))
      audio = mutagen.File(file_path, easy=False)
      if audio is None:
        continue
      f.duration = float(audio.info.length)
      f.bitrate = audio.info.bitrate or 0
      f.sample_rate = audio.info.sample_rate or 0
      f.channels = audio.info.channels or 0
      session.commit()
    except Exception as e:
      session.rollback()
      print(f'Failed to backfill metadata for {f.filename}: {e}')


def downgrade() -> None:
  pass
