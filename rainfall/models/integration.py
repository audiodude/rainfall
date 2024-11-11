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
    return {
        'has_netlify_token': self.netlify_access_token is not None,
    }

  def to_authlib_token(self, type_):
    if type_ != 'netlify':
      raise ValueError(f'Unsupported type: {type_}')

    return {
        'access_token': self.netlify_access_token,
        'refresh_token': self.netlify_refresh_token,
        'created_at': self.netlify_created_at,
        'token_type': 'Bearer',
        'scope': 'public',
    }
