import uuid

import pytest
from django.db import models

pytestmark = pytest.mark.django_db


def test_get_model_name(table_factory):
    id = uuid.uuid4()
    name = "table_name"
    table = table_factory(id=id, name=name)

    result = table.get_model_name()

    assert result == f"{name}_{str(id)}"


def test_get_model_returns_correct_model(table_factory, field_factory):
    table = table_factory()
    field1 = field_factory(table=table, name="field_1", type="BOOL")
    field2 = field_factory(table=table, name="field_2", type="CHAR")
    field3 = field_factory(table=table, name="field_3", type="INTEGER")

    result = table.get_model()

    assert result._meta.local_fields[1].name == field1.name
    assert result._meta.local_fields[2].name == field2.name
    assert result._meta.local_fields[3].name == field3.name
    assert type(result._meta.local_fields[1]) is models.BooleanField
    assert type(result._meta.local_fields[2]) is models.CharField
    assert type(result._meta.local_fields[3]) is models.IntegerField


def test_get_model_sets_default_app_id_field(table):
    result = table.get_model()

    assert result._meta.local_fields[0].name == "id"
    assert type(result._meta.local_fields[0]) is models.BigAutoField


def test_get_model_ommits_unsupported_fields(table_factory, field_factory):
    table = table_factory()
    field1 = field_factory(table=table, name="field_1", type="UUID")

    result = table.get_model()

    assert field1.name not in [field.name for field in result._meta.local_fields]
