from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg
from .models import (
    Category, Vendor, Tax, Unit, Location, Product, ProductVariant, 
    Stock, Customer, Order, OrderItem
)
from .serializers import (
    CategorySerializer, VendorSerializer, TaxSerializer, UnitSerializer, LocationSerializer,
    ProductSerializer, ProductVariantSerializer, StockSerializer, CustomerSerializer,
    OrderSerializer, OrderItemSerializer, CategorySummarySerializer, ProductSummarySerializer, StockSummarySerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for Category model"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['name', 'description', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get lightweight category summary for dropdowns"""
        categories = self.get_queryset()
        serializer = CategorySummarySerializer(categories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products for this category"""
        category = self.get_object()
        products = Product.objects.filter(category=category, is_active=True)
        serializer = ProductSummarySerializer(products, many=True)
        return Response(serializer.data)


class VendorViewSet(viewsets.ModelViewSet):
    """API endpoint for Vendor model"""
    queryset = Vendor.objects.filter(is_active=True)
    serializer_class = VendorSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['name', 'contact_person', 'email', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products from this vendor"""
        vendor = self.get_object()
        products = Product.objects.filter(vendor=vendor, is_active=True)
        serializer = ProductSummarySerializer(products, many=True)
        return Response(serializer.data)


class TaxViewSet(viewsets.ModelViewSet):
    """API endpoint for Tax model"""
    queryset = Tax.objects.filter(is_active=True)
    serializer_class = TaxSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'rate', 'created_at']
    ordering = ['name']


class UnitViewSet(viewsets.ModelViewSet):
    """API endpoint for Unit model"""
    queryset = Unit.objects.filter(is_active=True)
    serializer_class = UnitSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['name', 'symbol']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class LocationViewSet(viewsets.ModelViewSet):
    """API endpoint for Location model"""
    queryset = Location.objects.filter(is_active=True)
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['name', 'address', 'location_type']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """Get stock for this location"""
        location = self.get_object()
        stocks = Stock.objects.filter(location=location)
        serializer = StockSummarySerializer(stocks, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """API endpoint for Product model"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['name', 'description', 'variants__sku']
    filterset_fields = ['category', 'vendor', 'tax', 'unit']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """Get variants for this product"""
        product = self.get_object()
        variants = ProductVariant.objects.filter(product=product, is_active=True)
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """Get stock information for this product"""
        product = self.get_object()
        stocks = Stock.objects.filter(variant__product=product)
        serializer = StockSummarySerializer(stocks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        low_stock_threshold = 10
        products = Product.objects.filter(
            Q(variants__stock__quantity__lte=low_stock_threshold) |
            Q(variants__stock__quantity__isnull=True),
            is_active=True
        ).distinct()
        serializer = ProductSummarySerializer(products, many=True)
        return Response(serializer.data)


class ProductVariantViewSet(viewsets.ModelViewSet):
    """API endpoint for ProductVariant model"""
    queryset = ProductVariant.objects.filter(is_active=True)
    serializer_class = ProductVariantSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['sku', 'product__name', 'size_weight']
    filterset_fields = ['product', 'barcode']
    ordering_fields = ['sku', 'created_at', 'updated_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """Get stock information for this variant"""
        variant = self.get_object()
        stocks = Stock.objects.filter(variant=variant)
        serializer = StockSummarySerializer(stocks, many=True)
        return Response(serializer.data)


class StockViewSet(viewsets.ModelViewSet):
    """API endpoint for Stock model"""
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['variant__sku', 'variant__product__name', 'location__name']
    filterset_fields = ['variant', 'location', 'transaction_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get stock summary by location"""
        locations = Location.objects.filter(is_active=True)
        summary_data = []
        
        for location in locations:
            stocks = Stock.objects.filter(location=location)
            total_quantity = stocks.aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            summary_data.append({
                'location_id': location.id,
                'location_name': location.name,
                'total_quantity': total_quantity,
                'unique_products': stocks.values('variant__product').distinct().count()
            })
        
        return Response(summary_data)

    @action(detail=False, methods=['get'])
    def movements(self, request):
        """Get recent stock movements"""
        days = request.query_params.get('days', 7)
        from django.utils import timezone
        from datetime import timedelta
        
        start_date = timezone.now() - timedelta(days=int(days))
        movements = Stock.objects.filter(created_at__gte=start_date)
        serializer = StockSerializer(movements, many=True)
        return Response(serializer.data)


class CustomerViewSet(viewsets.ModelViewSet):
    """API endpoint for Customer model"""
    queryset = Customer.objects.filter(is_active=True)
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['name', 'email', 'phone']
    filterset_fields = ['tier']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Get orders for this customer"""
        customer = self.get_object()
        orders = Order.objects.filter(customer=customer)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get customer summary by tier"""
        customers = Customer.objects.filter(is_active=True)
        summary_data = customers.values('tier').annotate(
            count=Count('id')
        ).order_by('tier')
        
        return Response(list(summary_data))


class OrderViewSet(viewsets.ModelViewSet):
    """API endpoint for Order model"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['customer_name', 'id']
    filterset_fields = ['customer', 'status', 'order_type', 'payment_status', 'payment_method']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get items for this order"""
        order = self.get_object()
        items = OrderItem.objects.filter(order=order)
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get order summary statistics"""
        from django.utils import timezone
        from datetime import timedelta
        
        days = request.query_params.get('days', 30)
        start_date = timezone.now() - timedelta(days=int(days))
        
        orders = Order.objects.filter(created_at__gte=start_date)
        
        summary_data = {
            'total_orders': orders.count(),
            'total_amount': orders.aggregate(
                total=Sum('total_amount')
            )['total'] or 0,
            'by_status': orders.values('status').annotate(
                count=Count('id'),
                total_amount=Sum('total_amount')
            ).order_by('status'),
            'by_payment_status': orders.values('payment_status').annotate(
                count=Count('id'),
                total_amount=Sum('total_amount')
            ).order_by('payment_status'),
            'by_order_type': orders.values('order_type').annotate(
                count=Count('id'),
                total_amount=Sum('total_amount')
            ).order_by('order_type')
        }
        
        return Response(summary_data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's orders"""
        from django.utils import timezone
        from datetime import date
        
        today = date.today()
        orders = Order.objects.filter(created_at__date=today)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderItemViewSet(viewsets.ModelViewSet):
    """API endpoint for OrderItem model"""
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['variant__sku', 'variant__product__name', 'notes']
    filterset_fields = ['order', 'variant']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def popular_products(self, request):
        """Get most ordered products"""
        from django.db.models import Count
        
        days = request.query_params.get('days', 30)
        from django.utils import timezone
        from datetime import timedelta
        
        start_date = timezone.now() - timedelta(days=int(days))
        
        popular_products = OrderItem.objects.filter(
            order__created_at__gte=start_date
        ).values('variant__product').annotate(
            total_quantity=Sum('quantity'),
            order_count=Count('order')
        ).order_by('-total_quantity')[:10]
        
        return Response(list(popular_products))
