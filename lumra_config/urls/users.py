from django.urls import path
from lumra_config.views.inventory_views import users_view

urlpatterns = [
    path("", users_view, name="users"),
]