import pytest
from alembic.config import Config
from alembic import command


def test_alembic_migrations_run_without_errors():
    try:
        alembic_cfg = Config("alembic.ini")
        # Run alembic upgrade head programmatically
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        pytest.fail(f"Alembic migration failed with error: {e}")
