import environ
import pytest
from django.conf import settings
from django.db import connections
from pytest_factoryboy import register
from tables.tests.factories import FieldFactory
from tables.tests.factories import TableFactory

register(TableFactory)
register(FieldFactory)

env = environ.Env()


@pytest.fixture(scope="session", autouse=True)
def configure_test_db() -> None:
    del connections.__dict__["settings"]
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "db-test",
        "USER": env("TEST_POSTGRES_USER"),
        "PASSWORD": env("TEST_POSTGRES_PASSWORD"),
        "HOST": "postgresql-test",
        "PORT": 5432,
    }

    connections._settings = connections.configure_settings(settings.DATABASES)
    connections["default"] = connections.create_connection("default")
