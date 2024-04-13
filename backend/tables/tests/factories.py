import factory.fuzzy
from tables.models import Field
from tables.models import FieldsTypes
from tables.models import Table


class TableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Table

    id = factory.Faker("uuid4")
    name = factory.Faker("pystr")


class FieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Field

    id = factory.Faker("uuid4")
    name = factory.Faker("pystr")

    type = factory.fuzzy.FuzzyChoice(FieldsTypes, getter=lambda x: x)
