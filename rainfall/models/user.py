from typing import List
from dataclasses import dataclass, fields
from functools import partial

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid, String, Boolean
from uuid_extensions import uuid7

from rainfall.db import db
from rainfall.models.site import Site
from rainfall.models.integration import Integration


@dataclass
class User(db.Model):
  __tablename__ = 'users'

  id: Mapped[bytes] = mapped_column(Uuid, primary_key=True, default=uuid7)
  google_id: Mapped[str] = mapped_column(String(255),
                                         unique=True,
                                         nullable=True)

  mastodon_netloc: Mapped[str] = mapped_column(String(255), nullable=True)
  mastodon_id: Mapped[str] = mapped_column(String(255), nullable=True)
  mastodon_access_token: Mapped[str] = mapped_column(String(255), nullable=True)

  name: Mapped[str] = mapped_column(String(255), nullable=True)
  email: Mapped[str] = mapped_column(String(1024), nullable=True)
  picture_url: Mapped[str] = mapped_column(String(1024), nullable=True)
  is_welcomed: Mapped[bool] = mapped_column(Boolean, default=False)

  sites: Mapped[List['Site']] = relationship(back_populates='user')
  integration: Mapped['Integration'] = relationship(back_populates='user')

  def __repr__(self) -> str:
    return f'User(id={self.id!r}, google_id={self.google_id!r})'

  def serialize(self):
    props = []
    for field in fields(self):
      if field.name == 'sites':
        continue

      if field.name == 'integration' and self.integration is not None:
        props.append(('integration', self.integration.serialize()))
        continue

      props.append((field.name, getattr(self, field.name)))
    return dict(props)
