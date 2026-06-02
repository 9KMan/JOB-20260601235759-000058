"""
Alembic migration configuration
"""
import os
from alembic import context

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
db_url = os.getenv("DATABASE_URL", "")
config.set_main_option("sqlalchemy.url", db_url)

from models import Base

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode"""
    url = config.get_main_option("sqlalchemy.url")
    if url:
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode"""
    from sqlalchemy import engine_from_config

    section = config.get_section(config.config_ini_section) or {}
    connectable = engine_from_config(section, prefix="sqlalchemy.")

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()