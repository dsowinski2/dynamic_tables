from django.db import connection
from django.db import models
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Field
from .models import FieldsTypes
from .models import Table


fields_mapping = {
    "CHAR": models.CharField,
    "BOOL": models.BooleanField,
    "INTEGER": models.IntegerField,
}


class FieldSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False, default=None)
    name = serializers.CharField()
    type = serializers.ChoiceField(choices=FieldsTypes.choices)


class UpdateTableFieldsSerializer(serializers.Serializer):
    fields = FieldSerializer(many=True)

    @transaction.atomic
    def update(self, instances, validated_data):
        validated_data = validated_data["fields"]
        table = self.context["table"]
        operations = {"remove": [], "add": []}
        existing_fields = [field for field in validated_data if field.get("id")]
        instances_names = [instance.name for instance in instances]
        fields_to_delete = instances.exclude(
            id__in=[field["id"] for field in existing_fields]
        )
        fields_to_create = [field for field in validated_data if not field.get("id")]

        for field in fields_to_delete:
            operations["remove"].append(getattr(table.get_model(), field.name).field)
        fields_to_delete.delete()

        for field in fields_to_create:
            if field["name"] in instances_names:
                raise ValidationError(
                    f"Field with name {field['name']} already exists."
                )
            new_field = Field.objects.create(**field, table=table)
            operations["add"].append(getattr(table.get_model(), new_field.name).field)
            continue

        with connection.schema_editor() as schema_editor:
            self.edit_db_schema(schema_editor, table, operations)
        return table

    def edit_db_schema(self, schema_editor, table, operations):
        for operation_type, entities in operations.items():
            if operation_type == "add":
                for entity in entities:
                    schema_editor.add_field(table.get_model(), entity)
                    continue
            if operation_type == "remove":
                for entity in entities:
                    schema_editor.remove_field(table.get_model(), entity)
                    continue


class CreateTableSerialzer(serializers.Serializer):
    name = serializers.CharField()
    fields = FieldSerializer(many=True)

    def validate(self, attrs):
        if Table.objects.filter(name=attrs["name"]):
            raise ValidationError(f"Table with name: {attrs['name']} already exists.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        fields_data = validated_data.pop("fields")
        table = Table.objects.create(**validated_data)
        for field_data in fields_data:
            Field.objects.create(**field_data, table=table)
        table.schema_create_model()
        return table
