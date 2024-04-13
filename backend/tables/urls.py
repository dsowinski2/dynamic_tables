from django.urls import path

from .views import TablesView


urlpatterns = [
    path("table", TablesView.as_view({"post": "create"})),
    path("table/<uuid:id>", TablesView.as_view({"put": "update"})),
    path("table/<uuid:id>/row", TablesView.as_view({"post": "add_row"})),
    path("table/<uuid:id>/rows", TablesView.as_view({"get": "list"})),
]
