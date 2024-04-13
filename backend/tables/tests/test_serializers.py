import pytest
from rest_framework.exceptions import ValidationError
from tables.models import Field
from tables.models import Table
from tables.serializers import CreateTableSerialzer
from tables.serializers import FieldSerializer
from tables.serializers import UpdateTableFieldsSerializer

pytestmark = pytest.mark.django_db


class TestFieldSerializer:
    def test_unsupported_type_raises_validation_error(self):
        data = [{"name": "field_name_1", "type": "UUID"}]
        serializer = FieldSerializer(data=data, many=True)

        with pytest.raises(ValidationError) as err:
            serializer.is_valid(raise_exception=True)

        exceptions_list = err._excinfo[1].detail[0]["type"]
        assert len(exceptions_list) == 1
        assert exceptions_list[0] == '"UUID" is not a valid choice.'


@pytest.mark.django_db(transaction=True)
class TestCreateTableSerializer:
    def test_create_adds_table_and_fields_to_db(self):
        data = {
            "name": "Table1",
            "fields": [
                {"name": "field_name_1", "type": "BOOL", "attrs": {"null": True}},
                {"name": "field_name_2", "type": "CHAR", "attrs": {"null": True}},
            ],
        }
        serializer = CreateTableSerialzer(data=data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        assert len(Table.objects.all()) == 1


@pytest.mark.django_db(transaction=True)
class TestUpdateTableFieldsSerializer:
    DATA = {
        "fields": [
            {"name": "field_1", "type": "BOOL"},
        ]
    }

    def execute_serializer_update(self, table, data=None):
        data = data or self.DATA
        context = {"table": table}
        table.schema_create_model()
        serializer = UpdateTableFieldsSerializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.update(table.fields.all(), serializer.validated_data)

    def test_serializer_raises_for_duplicate_fields_names(self, table, field_factory):
        field_factory(table=table, name="field_1", type="BOOL")

        with pytest.raises(ValidationError) as err:
            self.execute_serializer_update(table)

        msg = err._excinfo[1].detail[0]
        assert msg == "Field with name field_1 already exists."

    @pytest.mark.django_db(transaction=True)
    def test_serializer_creates_new_field(self, table):
        self.execute_serializer_update(table)

        assert len(Field.objects.all()) == 1
        field = Field.objects.first()
        assert field.name == "field_1"
        assert field.type == "BOOL"

    def test_serializer_removes_not_specified_fields(self, table, field_factory):
        field_factory(table=table, name="field_1", type="BOOL")
        data = {"fields": []}
        self.execute_serializer_update(table, data)

        assert len(table.fields.all()) == 0

    @pytest.mark.django_db(transaction=True)
    def test_serializer_removes_and_adds_multiple_fields(self, table, field_factory):
        field_factory(table=table, name="field_1", type="CHAR")
        field_factory(table=table, name="field_2", type="INTEGER")

        data = {
            "fields": [
                {"name": "field_3", "type": "BOOL"},
                {"name": "field_4", "type": "BOOL"},
            ]
        }
        self.execute_serializer_update(table, data)

        assert len(table.fields.all()) == 2
        assert table.fields.filter(name="field_3").exists()
        assert table.fields.filter(name="field_4").exists()
