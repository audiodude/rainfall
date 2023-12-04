from dataclasses import dataclass, fields
from functools import partial
import re

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid, String
from uuid_extensions import uuid7

from rainfall.db import db

RE_NAME = re.compile(r'(.+)((_\d+)?\..+)')
RE_DUPE_NAME = re.compile(r'(.+)((_\d+)(\..+))')


@dataclass
class File(db.Model):
  __tablename__ = 'files'

  id: Mapped[bytes] = mapped_column(Uuid, primary_key=True, default=uuid7)
  release_id: Mapped[bytes] = mapped_column(ForeignKey("releases.id"))
  release: Mapped["Release"] = relationship(back_populates="files")
  filename: Mapped[str] = mapped_column(String(1024))
  original_filename: Mapped[str] = mapped_column(String(1024), nullable=True)

  def __repr__(self) -> str:
    return f'File(id={self.id!r}, release_id={self.release_id!r})'

  def serialize(self):
    return dict((field.name, getattr(self, field.name))
                for field in fields(self)
                if field.name != 'release')

  def _new_name(self):
    if self.release is None:
      raise ValueError('Cannot rename a file that does not belong to a release')

    dupe_file = None
    for f in self.release.files:
      if self is f:
        continue
      if self.filename == f.filename:
        dupe_file = f
        break

    if dupe_file is None:
      # Return whether rename was necessary.
      return False
    dupe_name = dupe_file.filename

    regex = RE_NAME if dupe_file.original_filename is None else RE_DUPE_NAME
    md = regex.match(dupe_name)
    if not md:
      raise ValueError(f'Invalid file, name={dupe_file.filename}, '
                       f'original_name={dupe_file.original_filename}')

    if dupe_file.original_filename is not None:
      # Increment the numerical part, minus the _
      num = int(md.group(3).split('_')[1]) + 1
      new_name = f'{md.group(1)}_{num}{md.group(4)}'
    else:
      # Add a _1 tag to the name
      new_name = f'{md.group(1)}_1{md.group(2)}'

    # Return whether rename was necessary.
    self.original_filename = self.filename
    self.filename = new_name
    return True

  def maybe_rename(self):
    # Keep trying names until a free one is found
    while self._new_name():
      pass
