from dotenv import load_dotenv

load_dotenv()

from logging.config import fileConfig
import os

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
  fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

from rainfall.db import Base
from rainfall.models.artwork import Artwork
from rainfall.models.file import File
from rainfall.models.integration import Integration
from rainfall.models.mastodon_credential import MastodonCredential
from rainfall.models.release import Release
from rainfall.models.site import Site
from rainfall.models.user import User

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_db_uri():
  return os.environ['SQLALCHEMY_DATABASE_URI']


def run_migrations_offline() -> None:
  """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
  url = config.get_main_option("sqlalchemy.url")
  context.configure(
      url=get_db_uri(),
      target_metadata=target_metadata,
      literal_binds=True,
      dialect_opts={"paramstyle": "named"},
  )

  with context.begin_transaction():
    context.run_migrations()


def run_migrations_online() -> None:
  """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
  connectable = create_engine(get_db_uri())

  with connectable.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
      context.run_migrations()


if context.is_offline_mode():
  run_migrations_offline()
else:
  run_migrations_online()
