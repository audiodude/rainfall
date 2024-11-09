from dataclasses import dataclass, fields
from functools import cached_property
import json

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid, String, Integer
from uuid_extensions import uuid7

from rainfall.db import db


@dataclass
class Integration(db.Model):
  __tablename__ = 'integrations'

  id: Mapped[bytes] = mapped_column(Uuid, primary_key=True, default=uuid7)
  user_id: Mapped[bytes] = mapped_column(ForeignKey('users.id'))
  user: Mapped['User'] = relationship(back_populates='integration')
  netlify_access_token: Mapped[str] = mapped_column(String(255), nullable=True)
  netlify_refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
  netlify_created_at: Mapped[str] = mapped_column(Integer, nullable=True)

  def serialize(self):
    props = []
    for field in fields(self):
      if field.name in ('user', 'user_id', 'id'):
        continue
      props.append((field.name, getattr(self, field.name)))

    return dict(props)
