from dataclasses import dataclass

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid, String
from uuid_extensions import uuid7

from rainfall.db import db


@dataclass
class Integration(db.Model):
  __tablename__ = 'integrations'

  id: Mapped[bytes] = mapped_column(Uuid, primary_key=True, default=uuid7)
  user_id: Mapped[bytes] = mapped_column(ForeignKey('users.id'))
  user: Mapped['User'] = relationship(back_populates='integration')
  netlify_access_token: Mapped[str] = mapped_column(String(255), nullable=True)
