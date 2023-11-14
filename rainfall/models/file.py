from dataclasses import dataclass, fields
from functools import partial

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid, String
from uuid_extensions import uuid7

from rainfall.db import db


@dataclass
class File(db.Model):
  __tablename__ = 'files'

  id: Mapped[bytes] = mapped_column(Uuid, primary_key=True, default=uuid7)
  release_id: Mapped[bytes] = mapped_column(ForeignKey("releases.id"))
  release: Mapped["Release"] = relationship(back_populates="files")
  filename: Mapped[str] = mapped_column(String(1024))

  def __repr__(self) -> str:
    return f'File(id={self.id!r}, release_id={self.release_id!r})'

  def serialize(self):
    return dict((field.name, getattr(self, field.name))
                for field in fields(self)
                if field.name != 'release')
