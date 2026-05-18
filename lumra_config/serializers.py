from rest_framework import serializers
from .models import (
    Category, Vendor, Tax, Unit, Location, Product, ProductVariant, 
    Stock, Customer, Order, OrderItem, UserProfile
)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent', 'slug', 'code', 'icon_url', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.parent:
            data['parent_name'] = instance.parent.name
        return data


class VendorSerializer(serializers.ModelSerializer):
    """Serializer for Vendor model"""
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'contact_person', 'phone', 'code', 'email', 'address', 'website', 'tax_number', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaxSerializer(serializers.ModelSerializer):
    """Serializer for Tax model"""
    class Meta:
        model = Tax
        fields = ['id', 'name', 'rate', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['rate_percentage'] = f"{instance.rate * 100}%"
        return data


class UnitSerializer(serializers.ModelSerializer):
    """Serializer for Unit model"""
    class Meta:
        model = Unit
        fields = ['id', 'name', 'symbol', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model"""
    class Meta:
        model = Location
        fields = ['id', 'name', 'address', 'location_type', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariant model"""
    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'size_weight', 'barcode', 'cost_price', 'selling_price', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'vendor', 'tax', 'unit', 'variants', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.category:
            data['category_name'] = instance.category.name
        if instance.vendor:
            data['vendor_name'] = instance.vendor.name
        if instance.tax:
            data['tax_name'] = instance.tax.name
        if instance.unit:
            data['unit_name'] = instance.unit.name
            data['unit_symbol'] = instance.unit.symbol
        return data


class StockSerializer(serializers.ModelSerializer):
    """Serializer for Stock model"""
    variant = ProductVariantSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    
    class Meta:
        model = Stock
        fields = ['id', 'variant', 'location', 'quantity', 'transaction_type', 'reference', 'created_at']
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.variant:
            data['variant_sku'] = instance.variant.sku
            data['variant_name'] = instance.variant.product.name
        if instance.location:
            data['location_name'] = instance.location.name
        return data


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model"""
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'address', 'tier', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tier_display'] = instance.get_tier_display()
        return data


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    variant = ProductVariantSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'variant', 'quantity', 'price', 'cost_price', 'discount_amount', 'discount_percent', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.variant:
            data['variant_sku'] = instance.variant.sku
            data['variant_name'] = instance.variant.product.name
        data['subtotal'] = instance.quantity * instance.price
        return data


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    customer = CustomerSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_name', 'status', 'order_type', 'payment_status', 'payment_method', 'paid_amount', 'change_amount', 'cashier', 'shift_id', 'table_number', 'dining_option', 'items', 'total_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['status_display'] = instance.get_status_display()
        data['order_type_display'] = instance.get_order_type_display()
        data['payment_status_display'] = instance.get_payment_status_display()
        data['payment_method_display'] = instance.get_payment_method_display()
        data['dining_option_display'] = instance.get_dining_option_display()
        
        # Calculate total amount from items
        total_amount = sum(item.quantity * item.price for item in instance.items.all())
        data['total_amount'] = total_amount
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = serializers.StringRelatedField(read_only=True)
    location = LocationSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'location', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.location:
            data['location_name'] = instance.location.name
        return data


# Summary Serializers for Dashboard
class CategorySummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for category lists"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'code', 'is_active']


class ProductSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'category_name', 'is_active']


class StockSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for stock lists"""
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    sku = serializers.CharField(source='variant.sku', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = Stock
        fields = ['id', 'sku', 'product_name', 'location_name', 'quantity', 'transaction_type']
