from dataclasses import dataclass
from functools import partial

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid
from uuid_extensions import uuid7

from rainfall.db import db


@dataclass
class Site(db.Model):
  __tablename__ = 'sites'

  id: Mapped[bytes] = mapped_column(Uuid, primary_key=True, default=uuid7)
  user_id: Mapped[bytes] = mapped_column(ForeignKey("users.id"))
  user: Mapped["User"] = relationship(back_populates="sites")

  def __repr__(self) -> str:
    return f'Site(id={self.id!r}, user_id={self.google_id!r})'
