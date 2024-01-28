from dataclasses import dataclass, fields
from functools import partial

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid, String, Text
from uuid_extensions import uuid7

from rainfall.db import db
from rainfall.models.release import Release


@dataclass
class Artwork(db.Model):
  __tablename__ = 'artwork'

  id: Mapped[bytes] = mapped_column(Uuid, primary_key=True, default=uuid7)
  filename: Mapped[str] = mapped_column(String(1024))

  release_id: Mapped["Release"] = mapped_column(ForeignKey("releases.id"))
  release: Mapped["Release"] = relationship(back_populates="artwork")

  def __repr__(self) -> str:
    return f'Artwork(id={self.id!r}, release_id={self.site.id!r}, name={self.name!r})'
