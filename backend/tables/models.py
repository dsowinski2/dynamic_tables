import uuid

from django.db import connection
from django.db import models
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer


class FieldsTypes(models.TextChoices):
    CHAR = ("CHAR", "char")
    INTEGER = ("INTEGER", "integer")
    BOOL = ("BOOL", "bool")


fields_mapping = {
    "CHAR": models.CharField,
    "BOOL": models.BooleanField,
    "INTEGER": models.IntegerField,
}


def validate(self, data):
    if hasattr(self, "initial_data"):
        for i in self.initial_data:
            unknown_keys = set(i.keys()) - set(self.fields.keys())
            if unknown_keys:
                raise ValidationError("Got unknown fields: {}".format(unknown_keys))
    return data


class Table(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(unique=True)

    def get_model_name(self):
        return f"{self.name}_{str(self.id)}"

    def get_model(self):
        attrs = {
            "Meta": type("Meta", (), {"app_label": "tables"}),
            "__module__": "database.models",
        }

        for field in self.fields.all():
            if field_type := fields_mapping.get(field.type):
                attrs[field.name] = field_type(null=True)

        model = type(self.get_model_name(), (models.Model,), attrs)
        return model

    def schema_create_model(self):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(self.get_model())

    def get_serializer_class(self):
        name = f"{self.get_model_name()}Serializer"
        serializer = type(
            name,
            (ModelSerializer,),
            {
                "validate": validate,
                "Meta": type(
                    "Meta", (), {"model": self.get_model(), "fields": "__all__"}
                ),
            },
        )
        return serializer


class Field(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField()
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="fields")
    type = models.CharField(choices=FieldsTypes.choices)
