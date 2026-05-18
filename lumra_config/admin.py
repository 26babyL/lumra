# lumra_config/admin.py
# Django Admin interfaces for LUMRA models

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F
from django.utils.timezone import now
from .models import (
    # Core Models
    Location, Product, Stock, Requisition, Transfer, UserProfile,
    Category, Vendor, Tax, Unit, Customer,
    ProductVariant, ProductAttribute,
    
    # Order Models
    Order, OrderItem,
    
    # 5 NEW CRITICAL MODELS
    StockMovement, Returns, ReturnItems, Payments, ProductBatches,
    
    # Stock Opname Models
    StockOpnameSession, StockOpnameItem,
)

# =========================
# ADMIN MIXINS
# =========================

class TimestampedAdminMixin:
    """Mixin for models with created_at/updated_at fields"""
    
    def created_at_display(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    created_at_display.short_description = 'Created'
    
    def updated_at_display(self, obj):
        if hasattr(obj, 'updated_at') and obj.updated_at:
            return obj.updated_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    updated_at_display.short_description = 'Updated'

class ReadOnlyAdminMixin:
    """Mixin for read-only admin views"""
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

# =========================
# CORE MODEL ADMINS
# =========================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'contact_person', 'email', 'code']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'symbol']
    readonly_fields = ['created_at']

@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ['name', 'rate', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'location_type', 'address']
    list_filter = ['location_type']
    search_fields = ['name', 'address']

@admin.register(Customer)
class CustomerAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'customer_type', 'tier', 'loyalty_points', 'total_spent', 'is_active']
    list_filter = ['customer_type', 'tier', 'is_active']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'last_order_date', 'average_order_value']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'phone', 'address', 'city')
        }),
        ('Customer Details', {
            'fields': ('customer_type', 'tier', 'is_active')
        }),
        ('Loyalty & Analytics', {
            'fields': ('loyalty_points', 'total_spent', 'total_orders', 'last_order_date'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'location', 'default_location_id', 'is_active']
    list_filter = ['role', 'is_active', 'location']
    search_fields = ['user__username', 'user__email', 'role']

# =========================
# PRODUCT MODEL ADMINS
# =========================

@admin.register(Product)
class ProductAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'category', 'vendor', 'unit', 'sell_price', 'barcode', 'min_stock', 'max_stock', 'is_active']
    list_filter = ['category', 'vendor', 'is_active', 'track_batch', 'has_expiry']
    search_fields = ['name', 'barcode', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'vendor', 'tax', 'unit')
        }),
        ('Pricing & Inventory', {
            'fields': ('sell_price', 'barcode', 'min_stock', 'max_stock', 'is_active')
        }),
        ('Tracking Options', {
            'fields': ('track_batch', 'has_expiry')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'size_weight', 'price_buy', 'price_sell']
    list_filter = ['product__category']
    search_fields = ['sku', 'product__name']
    raw_id_fields = ['product']

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['variant', 'attr_name', 'attr_value']
    list_filter = ['attr_name']
    search_fields = ['variant__sku', 'attr_name', 'attr_value']

# =========================
# INVENTORY MODEL ADMINS
# =========================

@admin.register(Stock)
class StockAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = ['variant', 'location', 'quantity', 'reserved_quantity', 'available_quantity', 'transaction_type']
    list_filter = ['location', 'transaction_type']
    search_fields = ['variant__sku', 'variant__product__name', 'location__name']
    readonly_fields = ['created_at', 'last_updated', 'available_quantity']

@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'requested_by', 'from_location', 'to_location', 'status', 'created_at']
    list_filter = ['status', 'from_location', 'to_location']
    search_fields = ['requested_by__username']
    readonly_fields = ['created_at']

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ['id', 'source_location', 'destination_location', 'status', 'created_at']
    list_filter = ['status', 'source_location', 'destination_location']
    search_fields = ['id']
    readonly_fields = ['created_at']

# =========================
# ORDER MODEL ADMINS
# =========================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['variant', 'quantity', 'price', 'cost_price', 'discount_amount', 'discount_percent', 'batch_id', 'notes']
    raw_id_fields = ['variant', 'batch_id']

@admin.register(Order)
class OrderAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer', 'order_type', 'status', 'payment_status', 'total_price', 'created_at_display']
    list_filter = ['order_type', 'status', 'payment_status', 'dining_option', 'created_at']
    search_fields = ['customer_name', 'customer__name', 'id']
    readonly_fields = ['created_at', 'total_price']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'customer_name', 'status', 'order_type')
        }),
        ('Payment Details', {
            'fields': ('payment_status', 'payment_method', 'paid_amount', 'change_amount')
        }),
        ('Service Details', {
            'fields': ('cashier_id', 'shift_id', 'table_number', 'dining_option')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'variant', 'quantity', 'price', 'cost_price', 'discount_amount', 'total_price']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__id', 'variant__sku', 'variant__product__name']
    raw_id_fields = ['order', 'variant', 'batch_id']
    
    def total_price(self, obj):
        return obj.quantity * obj.price
    total_price.short_description = 'Total Price'

# =========================
# 5 NEW CRITICAL MODEL ADMINS
# =========================

@admin.register(StockMovement)
class StockMovementAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = ['reference_number', 'product', 'location', 'movement_type', 'quantity', 'reference_type', 'created_at_display']
    list_filter = ['movement_type', 'reference_type', 'location', 'created_at']
    search_fields = ['reference_number', 'notes']
    readonly_fields = ['created_at']
    raw_id_fields = ['product', 'location']
    
    fieldsets = (
        ('Movement Information', {
            'fields': ('reference_number', 'product', 'location', 'movement_type', 'quantity')
        }),
        ('Reference Details', {
            'fields': ('reference_type', 'reference_id', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

class ReturnItemsInline(admin.TabularInline):
    model = ReturnItems
    extra = 1
    fields = ['product', 'quantity', 'reason', 'notes']
    raw_id_fields = ['product']

@admin.register(Returns)
class ReturnsAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = ['retur_number', 'customer', 'order', 'status', 'total_amount', 'created_at_display']
    list_filter = ['status', 'created_at', 'customer']
    search_fields = ['retur_number', 'customer__name', 'order__id']
    readonly_fields = ['created_at', 'total_amount']
    inlines = [ReturnItemsInline]
    raw_id_fields = ['customer', 'order']
    
    fieldsets = (
        ('Return Information', {
            'fields': ('retur_number', 'customer', 'order', 'status')
        }),
        ('Financial Details', {
            'fields': ('total_amount', 'refund_method', 'refund_reference')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(ReturnItems)
class ReturnItemsAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'quantity', 'reason']
    list_filter = ['reason']
    search_fields = ['id']
    raw_id_fields = ['retur_header', 'product']

@admin.register(Payments)
class PaymentsAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = ['payment_number', 'order', 'payment_method', 'amount', 'status', 'payment_date', 'created_at_display']
    list_filter = ['payment_method', 'status', 'payment_date', 'created_at']
    search_fields = ['payment_number', 'order__id', 'reference_number']
    readonly_fields = ['created_at', 'payment_number']
    raw_id_fields = ['order']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_number', 'order', 'payment_method', 'amount')
        }),
        ('Status & Reference', {
            'fields': ('status', 'reference_number', 'notes')
        }),
        ('Timestamps', {
            'fields': ('payment_date', 'created_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(ProductBatches)
class ProductBatchesAdmin(TimestampedAdminMixin, admin.ModelAdmin):
    list_display = ['batch_number', 'product', 'location', 'quantity_available', 'expiry_date', 'is_expired_display', 'created_at_display']
    list_filter = ['product', 'location', 'expiry_date']
    search_fields = ['batch_number', 'product__name', 'supplier_batch_number']
    readonly_fields = ['created_at']
    raw_id_fields = ['product', 'location']
    
    def is_expired_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">⚠️ Expired</span>')
        return format_html('<span style="color: green;">✅ Valid</span>')
    is_expired_display.short_description = 'Status'
    
    fieldsets = (
        ('Batch Information', {
            'fields': ('batch_number', 'product', 'location', 'quantity_available')
        }),
        ('Date Information', {
            'fields': ('manufacture_date', 'expiry_date')
        }),
        ('Supplier Information', {
            'fields': ('supplier_batch_number', 'supplier', 'cost_price')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

# =========================
# STOCK OPNAME MODEL ADMINS
# =========================

@admin.register(StockOpnameSession)
class StockOpnameSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'location', 'created_at']
    search_fields = ['id', 'location__name']
    readonly_fields = ['created_at']

@admin.register(StockOpnameItem)
class StockOpnameItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'variant', 'current_stock', 'counted_qty', 'difference']
    list_filter = ['session', 'variant']
    search_fields = ['id', 'variant__sku']
    raw_id_fields = ['session', 'variant']

# =========================
# ADMIN CUSTOMIZATION
# =========================

# Customize admin site
admin.site.site_header = "LUMRA ERP Administration"
admin.site.site_title = "LUMRA Admin"
admin.site.index_title = "Welcome to LUMRA ERP System Administration"