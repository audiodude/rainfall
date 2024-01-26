from typing import List
from dataclasses import dataclass, fields
from functools import partial

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid, String, Text
from uuid_extensions import uuid7

from rainfall.db import db


@dataclass
class Release(db.Model):
  __tablename__ = 'releases'

  id: Mapped[bytes] = mapped_column(Uuid, primary_key=True, default=uuid7)
  site_id: Mapped[bytes] = mapped_column(ForeignKey("sites.id"))
  site: Mapped["Site"] = relationship(back_populates="releases")
  name: Mapped[str] = mapped_column(String(255))
  description: Mapped[str] = mapped_column(Text, nullable=True)

  files: Mapped[List["File"]] = relationship(back_populates="release")

  def __repr__(self) -> str:
    return f'Release(id={self.id!r}, site_id={self.site_id!r})'

  def serialize(self):
    props = []
    for field in fields(self):
      if field.name == 'site':
        continue

      if field.name == 'files':
        props.append(('files', [file.serialize() for file in self.files]))
        continue

      props.append((field.name, getattr(self, field.name)))
    return dict(props)
