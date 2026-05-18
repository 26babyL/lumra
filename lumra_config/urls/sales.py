from django.urls import path
# POS view and related endpoints live in misc_views rather than
# inventory_views (the earlier import was incorrect and meant the
# `pos_view` in misc_views never got wired up).
from lumra_config.views.misc_views import (
    pos_view,
    pos_create_order,
    sales_history_view,
    sales_history_products_view,
    sales_performance_view,
    customers_view,
    add_customer_view,
    view_customer_view,
    edit_customer_view,
    delete_customer_view,
)

urlpatterns = [
    path("pos/", pos_view, name="pos"),
    path("pos/create-order/", pos_create_order, name="pos_create_order"),
    path("history/", sales_history_view, name="sales_history"),
    path("history/products/", sales_history_products_view, name="sales_history_products"),
    path("performance/", sales_performance_view, name="sales_performance"),
    path("customers/", customers_view, name="customers"),
    path("customers/add/", add_customer_view, name="add_customer"),
    path("customers/<int:customer_id>/", view_customer_view, name="view_customer"),
    path("customers/<int:customer_id>/edit/", edit_customer_view, name="edit_customer"),
    path("customers/<int:customer_id>/delete/", delete_customer_view, name="delete_customer"),
]