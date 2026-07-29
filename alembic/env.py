from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

from app.core.config import settings
from app.database import Base

load_dotenv()

# Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    database_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

    if database_url and database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    database_url = os.getenv("DATABASE_URL")

    # 1. Grab base config section as a mutable dictionary
    configuration = config.get_section(config.config_ini_section, {})

    # 2. Fix prefix and reassign back to database_url
    if database_url:
        if database_url.startswith("postgresql+asyncpg://"):
            database_url = database_url.replace(
                "postgresql+asyncpg://", "postgresql://", 1
            )
        elif database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        # 3. Inject into configuration dictionary
        configuration["sqlalchemy.url"] = database_url

    # 4. Pass the modified 'configuration' dictionary here!
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
