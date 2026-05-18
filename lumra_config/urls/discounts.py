from django.urls import path
from lumra_config.views.inventory_views import (
    discount_list_view,
    add_discount_view,
    edit_discount_view,
    delete_discount_view,
)

urlpatterns = [
    path("", discount_list_view, name="discount_list"),
    path("add/", add_discount_view, name="add_discount"),
    path("<int:discount_id>/edit/", edit_discount_view, name="edit_discount"),
    path("<int:discount_id>/delete/", delete_discount_view, name="delete_discount"),
]