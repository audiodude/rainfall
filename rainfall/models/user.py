from functools import partial

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid, String
from uuid_extensions import uuid7

from rainfall.db import Base


class User(Base):
  __tablename__ = 'users'

  id: Mapped[bytes] = mapped_column(Uuid, primary_key=True, default=uuid7)
  google_id: Mapped[str] = mapped_column(String(255), unique=True)

  def __repr__(self) -> str:
    return f'User(id={self.id!r}, google_id={self.google_id!r})'
