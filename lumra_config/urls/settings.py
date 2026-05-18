from django.urls import path
from lumra_config.views.inventory_views import (
    profile_view,
    settings_view,
    system_status_view,
    business_settings_view,
)

urlpatterns = [
    path("profile/", profile_view, name="profile"),
    path("settings/", settings_view, name="settings"),
    path("settings/system/", system_status_view, name="system_status"),
    path("settings/business/", business_settings_view, name="business_settings"),
]