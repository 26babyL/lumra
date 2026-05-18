from django.urls import path
from lumra_config.views.inventory_views import (
    about_view,
    contact_view,
    pricing_view,
    search_view,
)

urlpatterns = [
    path("about/", about_view, name="about"),
    path("contact/", contact_view, name="contact"),
    path("pricing/", pricing_view, name="pricing"),
    path("search/", search_view, name="search"),
]