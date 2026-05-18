from django.urls import path
from lumra_config.views.inventory_views import (
    campaign_list_view,
    add_campaign_view,
    edit_campaign_view,
    delete_campaign_view,
)

urlpatterns = [
    path("", campaign_list_view, name="campaign_list"),
    path("add/", add_campaign_view, name="add_campaign"),
    path("<int:campaign_id>/edit/", edit_campaign_view, name="edit_campaign"),
    path("<int:campaign_id>/delete/", delete_campaign_view, name="delete_campaign"),
]