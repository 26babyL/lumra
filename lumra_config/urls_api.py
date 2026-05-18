from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import (
    CategoryViewSet, VendorViewSet, TaxViewSet, UnitViewSet, LocationViewSet,
    ProductViewSet, ProductVariantViewSet, StockViewSet, CustomerViewSet,
    OrderViewSet, OrderItemViewSet
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'vendors', VendorViewSet, basename='vendor')
router.register(r'taxes', TaxViewSet, basename='tax')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-variants', ProductVariantViewSet, basename='productvariant')
router.register(r'stocks', StockViewSet, basename='stock')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/v1/', include(router.urls)),
]
