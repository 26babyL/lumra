from django.urls import path
from lumra_config.views.inventory_views import purchasing_view

urlpatterns = [
    path("", purchasing_view, name="purchasing"),
]