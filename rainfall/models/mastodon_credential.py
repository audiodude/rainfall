from typing import List
from dataclasses import dataclass, fields
from functools import partial

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid, String
from uuid_extensions import uuid7

from rainfall.db import db
from rainfall.models.release import Release


@dataclass
class MastodonCredential(db.Model):
  __tablename__ = 'mastodon_credentials'

  id: Mapped[bytes] = mapped_column(Uuid, primary_key=True, default=uuid7)
  netloc: Mapped[str] = mapped_column(String(255))
  client_id: Mapped[str] = mapped_column(String(255))
  client_secret: Mapped[str] = mapped_column(String(255))

  def __repr__(self) -> str:
    return f'MastodonCredential(id={self.id!r}, host={self.host!r})'
