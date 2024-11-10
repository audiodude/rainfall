from typing import List
from dataclasses import dataclass, fields

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid, String, Text
from uuid_extensions import uuid7

from rainfall.db import db
from rainfall.models.release import Release


@dataclass
class Site(db.Model):
  __tablename__ = 'sites'

  id: Mapped[bytes] = mapped_column(Uuid, primary_key=True, default=uuid7)
  user_id: Mapped[bytes] = mapped_column(ForeignKey('users.id'))
  user: Mapped['User'] = relationship(back_populates='sites')
  name: Mapped[str] = mapped_column(String(255))
  description: Mapped[str] = mapped_column(Text, nullable=True)

  netlify_site_id: Mapped[str] = mapped_column(String(255), nullable=True)
  netlify_url: Mapped[str] = mapped_column(String(255), nullable=True)

  releases: Mapped[List['Release']] = relationship(back_populates='site',
                                                   cascade='all, delete-orphan')

  def __repr__(self) -> str:
    return f'Site(id={self.id!r}, user_id={self.user_id!r}, name={self.name!r})'

  def serialize(self):
    props = []
    for field in fields(self):
      if field.name == 'user':
        continue

      if field.name == 'releases':
        props.append(
            ('releases', [release.serialize() for release in self.releases]))
        continue

      props.append((field.name, getattr(self, field.name)))
    return dict(props)
