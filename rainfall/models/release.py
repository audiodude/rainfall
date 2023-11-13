from dataclasses import dataclass, fields
from functools import partial

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid, String
from uuid_extensions import uuid7

from rainfall.db import db


@dataclass
class Release(db.Model):
  __tablename__ = 'releases'

  id: Mapped[bytes] = mapped_column(Uuid, primary_key=True, default=uuid7)
  site_id: Mapped[bytes] = mapped_column(ForeignKey("sites.id"))
  site: Mapped["Site"] = relationship(back_populates="releases")
  name: Mapped[str] = mapped_column(String(255))

  def __repr__(self) -> str:
    return f'Release(id={self.id!r}, site_id={self.site!r})'

  def serialize(self):
    return dict((field.name, getattr(self, field.name))
                for field in fields(self)
                if field.name != 'site')
