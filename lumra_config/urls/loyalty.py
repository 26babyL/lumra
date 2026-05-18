from django.urls import path
from lumra_config.views.inventory_views import (
    loyalty_members_view,
    add_loyalty_member_view,
    edit_loyalty_member_view,
    delete_loyalty_member_view,
)

urlpatterns = [
    path("", loyalty_members_view, name="loyalty_members"),
    path("add/", add_loyalty_member_view, name="add_loyalty_member"),
    path("<int:member_id>/edit/", edit_loyalty_member_view, name="edit_loyalty_member"),
    path("<int:member_id>/delete/", delete_loyalty_member_view, name="delete_loyalty_member"),
]