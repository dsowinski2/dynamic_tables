from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import Response
from rest_framework.viewsets import ViewSet

from .models import Table
from .serializers import CreateTableSerialzer
from .serializers import UpdateTableFieldsSerializer


class TablesView(ViewSet):
    def list(self, request, id):
        table = Table.objects.get(pk=id)
        table_model = table.get_model()
        serializer_class = table.get_serializer_class()
        serializer = serializer_class(table_model.objects.all(), many=True)

        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, id):
        table = Table.objects.get(pk=id)
        context = {"table": table}
        fields = table.fields.all()
        serializer = UpdateTableFieldsSerializer(
            fields, data=request.data, context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def create(self, request):
        serializer = CreateTableSerialzer(data=request.data)
        serializer.is_valid(raise_exception=True)
        table = serializer.save()
        return Response(str(table.id))

    @action(detail=True, methods=["POST"], name="add_row")
    def add_row(self, request, id):
        table = Table.objects.get(pk=id)
        serializer_class = table.get_serializer_class()
        serializer = serializer_class(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_201_CREATED, data=serializer.validated_data)
