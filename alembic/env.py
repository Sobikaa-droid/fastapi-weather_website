# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
import asyncio

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from src import database

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

load_dotenv()

config = context.config


def get_database_url():
    # Option A: Use the expanded DATABASE_URL from .env
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url

    # Option B: Construct from individual variables (fallback)
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')

    return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Set the dynamic database URL in Alembic configuration
config.set_main_option("sqlalchemy.url", get_database_url())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = database.Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context."""

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()