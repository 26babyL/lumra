# your_app/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models_expansion import (
       PurchaseOrder, PurchaseOrderItem,
       GoodsReceipt, GoodsReceiptItem,
       CustomerRFMScore,
       Promotion, PromotionUsage,
       SalesDaily, SalesMonthly,
       ProductPerformance, InventorySnapshot,
       Shift, ShiftSalesSummary,
       DashboardKPICache, AuditTrail,
   )
# =========================
# MODEL PENDUKUNG
# =========================

class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    parent      = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    slug        = models.CharField(max_length=100, unique=True, null=True, blank=True)
    code        = models.CharField(max_length=10, null=True, blank=True)
    icon_url    = models.CharField(max_length=255, null=True, blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        db_table = 'lumra_config_categories'


class Vendor(models.Model):
    name           = models.CharField(max_length=100, unique=True, db_index=True)
    contact_person = models.CharField(max_length=100, blank=True)
    phone          = models.CharField(max_length=20, blank=True)
    code           = models.CharField(max_length=20, blank=True, null=True)
    email          = models.EmailField(max_length=100, blank=True)
    address        = models.TextField(blank=True)
    website        = models.URLField(max_length=255, blank=True)
    tax_number     = models.CharField(max_length=50, blank=True)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'lumra_config_vendors'


class Tax(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    rate        = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.rate * 100}%)"

    class Meta:
        db_table = 'lumra_config_taxes'


class Unit(models.Model):
    name        = models.CharField(max_length=50, unique=True)
    symbol      = models.CharField(max_length=10, blank=True)  # renamed from short_name → symbol (konsisten dengan template)
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'lumra_config_units'


# =========================
# MODEL UTAMA
# =========================

class Location(models.Model):
    name          = models.CharField(max_length=100, unique=True, db_index=True)
    address       = models.TextField(blank=True)
    location_type = models.CharField(max_length=20, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'lumra_config_locations'


class Product(models.Model):
    name        = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    vendor      = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    tax         = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)
    unit        = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    
    # 🟢 FIELD EXTENSIONS (16 Apr 2026)
    sell_price  = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Harga jual standar')
    barcode     = models.CharField(max_length=100, null=True, blank=True, unique=True, db_index=True, help_text='Barcode/SKU produk')
    min_stock   = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Stok minimal sebelum alert')
    max_stock   = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Stok maksimal untuk autoorder')
    is_active   = models.BooleanField(default=True, db_index=True, help_text='Status aktif/nonaktif')
    track_batch = models.BooleanField(default=False, help_text='Apakah produk perlu tracking batch?')
    has_expiry  = models.BooleanField(default=False, help_text='Apakah produk bisa expired?')
    
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'lumra_config_products'


class ProductVariant(models.Model):
    product     = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    sku         = models.CharField(max_length=50, unique=True, db_index=True)
    size_weight = models.CharField(max_length=50, null=True, blank=True)
    price_buy   = models.DecimalField(max_digits=12, decimal_places=2)
    price_sell  = models.DecimalField(max_digits=12, decimal_places=2)
    updated_at  = models.DateTimeField(auto_now=True)

    @property
    def total_stock(self):
        """
        Hitung total stok dari semua lokasi.
        Jika view sudah annotate `_cached_total_stock`, pakai itu
        untuk menghindari query tambahan.
        """
        if hasattr(self, '_cached_total_stock'):
            return self._cached_total_stock
        return self.stock_entries.aggregate(total=Sum('quantity'))['total'] or 0

    @total_stock.setter
    def total_stock(self, value):
        """Store total_stock value in _cached_total_stock to avoid conflicts with annotation."""
        self._cached_total_stock = value

    def __str__(self):
        return self.sku

    class Meta:
        db_table = 'lumra_config_productvariants'


class ProductAttribute(models.Model):
    variant    = models.ForeignKey(ProductVariant, related_name='attributes', on_delete=models.CASCADE)
    attr_name  = models.CharField(max_length=100)
    attr_value = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.attr_name}: {self.attr_value}"

    class Meta:
        db_table = 'lumra_config_productattribute_items'


class Stock(models.Model):
    TRANSACTION_TYPES = (
        ('in',                'Stock In'),
        ('out',               'Stock Out'),
        ('adjustment',        'Adjustment'),
        ('transfer_sent',     'Transfer Sent'),
        ('transfer_received', 'Transfer Received'),
    )

    variant          = models.ForeignKey(ProductVariant, related_name='stock_entries', on_delete=models.CASCADE)
    location         = models.ForeignKey(Location, on_delete=models.CASCADE)
    quantity         = models.IntegerField(default=0)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    notes            = models.TextField(blank=True)
    
    # 🟢 FIELD EXTENSIONS (16 Apr 2026)
    reserved_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Qty yang di-reserve/hold')
    
    last_updated     = models.DateTimeField(auto_now=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    
    @property
    def available_quantity(self):
        '''Computed field: available = quantity - reserved'''
        return max(self.quantity - self.reserved_quantity, 0)

    def __str__(self):
        return f"{self.variant.sku} - {self.location.name}: {self.quantity}"

    class Meta:
        db_table = 'lumra_config_stock'
        indexes  = [models.Index(fields=['variant', 'location'])]


class Requisition(models.Model):
    STATUS_CHOICES = [
        ('waiting',    'Waiting Approval'),
        ('approved',   'Approved'),
        ('in_transit', 'In Transit'),
        ('completed',  'Completed'),
        ('rejected',   'Rejected'),
    ]

    from_location = models.ForeignKey(Location, related_name='requisitions_from', on_delete=models.CASCADE)
    to_location   = models.ForeignKey(Location, related_name='requisitions_to',   on_delete=models.CASCADE)
    requested_by  = models.ForeignKey(User, related_name='requested_requisitions', on_delete=models.CASCADE)
    approved_by   = models.ForeignKey(User, related_name='approved_requisitions',  null=True, blank=True, on_delete=models.SET_NULL)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    created_at    = models.DateTimeField(auto_now_add=True)
    approved_at   = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Requisition {self.id} from {self.from_location.name}"

    class Meta:
        db_table = 'lumra_config_requisitions'


class RequisitionItem(models.Model):
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE, related_name='items')
    variant     = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity    = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.variant.sku} x {self.quantity}"

    class Meta:
        unique_together = ('requisition', 'variant')
        db_table        = 'lumra_config_requisitionitem'


class Transfer(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('in_transit', 'In Transit'),
        ('received',   'Received'),
        ('cancelled',  'Cancelled'),
    ]

    requisition          = models.OneToOneField(Requisition, on_delete=models.CASCADE, null=True, blank=True)
    source_location      = models.ForeignKey(Location, related_name='transfers_from', on_delete=models.CASCADE)
    destination_location = models.ForeignKey(Location, related_name='transfers_to',   on_delete=models.CASCADE)
    created_by           = models.ForeignKey(User, on_delete=models.CASCADE)
    status               = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes                = models.TextField(blank=True)
    created_at           = models.DateTimeField(auto_now_add=True)
    sent_at              = models.DateTimeField(null=True, blank=True)
    received_at          = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transfer {self.id} to {self.destination_location.name}"

    class Meta:
        db_table = 'lumra_config_transfers'


class TransferItem(models.Model):
    transfer           = models.ForeignKey(Transfer, on_delete=models.CASCADE, related_name='items')
    variant            = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity_sent      = models.PositiveIntegerField()
    quantity_received  = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.variant.sku} x {self.quantity_sent}"

    class Meta:
        db_table = 'lumra_config_transferitem'


class UserProfile(models.Model):
    user     = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    
    # 🟢 FIELD EXTENSIONS (16 Apr 2026)
    role = models.CharField(max_length=100, blank=True, help_text='Role/jabatan pengguna')
    default_location_id = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL, related_name='users_default_location', help_text='Lokasi default')
    is_active = models.BooleanField(default=True, db_index=True, help_text='Status aktif/nonaktif')

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'lumra_config_userprofile'


# =========================
# SYSTEM SECURITY & SETTINGS
# =========================

class Role(models.Model):
    ROLE_TYPES = [
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("service", "Service"),
    ]

    name = models.CharField(max_length=100, unique=True, db_index=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    role_type = models.CharField(max_length=20, choices=ROLE_TYPES, default="staff")
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_roles"
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lumra_role_assignments")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_assignments")
    assigned_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_roles",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_user_roles"
        unique_together = ("user", "role")
        ordering = ["user__username", "role__name"]

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


class RolePermission(models.Model):
    ACCESS_LEVELS = [
        ("none", "None"),
        ("view", "View"),
        ("full", "Full"),
    ]

    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    module_key = models.CharField(max_length=50, db_index=True)
    module_name = models.CharField(max_length=100)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default="none")
    can_create = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_role_permissions"
        unique_together = ("role", "module_key")
        ordering = ["role__name", "module_name"]

    def __str__(self):
        return f"{self.role.name} - {self.module_name}"


class APIKey(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("revoked", "Revoked"),
        ("expired", "Expired"),
    ]

    name = models.CharField(max_length=120)
    key_prefix = models.CharField(max_length=20, db_index=True)
    hashed_key = models.CharField(max_length=128, unique=True)
    last_four = models.CharField(max_length=4, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_api_keys")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_api_keys"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def masked_key(self):
        suffix = self.last_four or "****"
        return f"{self.key_prefix}****{suffix}"

    @property
    def is_expired(self):
        return bool(self.expires_at and self.expires_at <= timezone.now())


class NumberingSequence(models.Model):
    key = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=120)
    prefix = models.CharField(max_length=30)
    digits = models.PositiveSmallIntegerField(default=4)
    current_value = models.PositiveIntegerField(default=0)
    reset_period = models.CharField(max_length=20, default="never")
    use_date_prefix = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_numbering_sequences"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.prefix})"


class EmailSetting(models.Model):
    encryption = models.CharField(max_length=20, default="tls")
    host = models.CharField(max_length=255, blank=True)
    port = models.PositiveIntegerField(default=587)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    from_name = models.CharField(max_length=120, blank=True)
    from_email = models.EmailField(blank=True)
    enabled = models.BooleanField(default=False)
    test_recipient = models.EmailField(blank=True)
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="updated_email_settings")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_email_settings"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.from_email or "Email Settings"


class NotificationSetting(models.Model):
    key = models.CharField(max_length=50, unique=True, db_index=True)
    label = models.CharField(max_length=120)
    email_enabled = models.BooleanField(default=False)
    app_enabled = models.BooleanField(default=False)
    whatsapp_enabled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="updated_notification_settings")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_notification_settings"
        ordering = ["label"]

    def __str__(self):
        return self.label


class BackupRecord(models.Model):
    STATUS_CHOICES = [
        ("ready", "Ready"),
        ("processing", "Processing"),
        ("failed", "Failed"),
        ("restored", "Restored"),
    ]

    name = models.CharField(max_length=255)
    backup_type = models.CharField(max_length=30, default="manual")
    file_path = models.CharField(max_length=255, blank=True)
    file_size_bytes = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ready", db_index=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_backup_records")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_backup_records"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def size_display(self):
        size = self.file_size_bytes or 0
        if size >= 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
        if size >= 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        if size >= 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size} B"


# =========================
# CUSTOMER / MEMBER MODEL
# =========================

class Customer(models.Model):
    TIER_CHOICES = [
        ('bronze',   'Bronze'),
        ('silver',   'Silver'),
        ('gold',     'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    CUSTOMER_TYPE_CHOICES = [
        ('retail', 'Retail/Personal'),
        ('wholesale', 'Wholesale'),
        ('restaurant', 'Restaurant'),
        ('hotel', 'Hotel'),
        ('clinic', 'Clinic'),
    ]

    name             = models.CharField(max_length=255, db_index=True)
    email            = models.EmailField(unique=True, db_index=True)
    phone            = models.CharField(max_length=20, blank=True)
    address          = models.TextField(blank=True)
    city             = models.CharField(max_length=100, blank=True)
    
    # 🟢 FIELD EXTENSIONS (16 Apr 2026)
    customer_type    = models.CharField(max_length=50, choices=CUSTOMER_TYPE_CHOICES, default='retail', help_text='Tipe customer')
    
    tier             = models.CharField(max_length=20, choices=TIER_CHOICES, default='bronze')
    loyalty_points   = models.IntegerField(default=0)
    total_spent      = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_orders     = models.IntegerField(default=0)
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)
    last_order_date  = models.DateTimeField(null=True, blank=True)

    @property
    def average_order_value(self):
        if self.total_orders > 0:
            return self.total_spent / self.total_orders
        return 0

    # compatibility helpers used by newer templates/views
    @property
    def whatsapp(self):
        """alias used by templates; backed by ``phone`` field."""
        return self.phone

    @property
    def points(self):
        """alias for loyalty points (templates refer to ``points``)."""
        return self.loyalty_points

    @property
    def lifetime_value(self):
        """total value of customer, used in detail footer."""
        return self.total_spent

    @property
    def last_visit(self):
        """alias used in templates for most recent visit/order date."""
        return self.last_order_date

    @property
    def points_expiry(self):
        """placeholder property; expiry not tracked in current model."""
        return None

    @property
    def iseller_id(self):
        """placeholder used in form/display; always ``None`` for now."""
        return None

    def __str__(self):
        return f"{self.name} ({self.tier.upper()})"

    class Meta:
        db_table = 'lumra_config_customers'
        ordering = ['-created_at']


# =========================
# ORDER MODEL
# =========================

class Order(models.Model):
    ORDER_TYPES = [
        ('draft', 'Draft/Quotation'),
        ('sales_order', 'Sales Order'),
        ('invoiced', 'Invoice'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Tunai'),
        ('debit_card', 'Kartu Debit'),
        ('credit_card', 'Kartu Kredit'),
        ('qris', 'QRIS'),
        ('bank_transfer', 'Transfer Bank'),
        ('check', 'Cek'),
        ('other', 'Lainnya'),
    ]
    
    DINING_OPTIONS = [
        ('dine_in', 'Makan di Tempat'),
        ('takeaway', 'Bungkus'),
        ('delivery', 'Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer      = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=100)  # kept for backward compatibility
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 🟢 FIELD EXTENSIONS (16 Apr 2026)
    order_type    = models.CharField(max_length=20, choices=ORDER_TYPES, default='sales_order', db_index=True, help_text='Tipe order')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', db_index=True, help_text='Status pembayaran')
    payment_method = models.CharField(max_length=50, blank=True, help_text='Metode pembayaran')
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Juml yang sudah dibayar')
    change_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Uang kembalian')
    cashier_id = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders_as_cashier', help_text='Kasir yang handle')
    shift_id = models.CharField(max_length=50, blank=True, help_text='ID shift kasir')
    table_number = models.CharField(max_length=20, blank=True, help_text='Nomor meja (untuk dining in)')
    dining_option = models.CharField(max_length=20, choices=DINING_OPTIONS, blank=True, help_text='Opsi makan')
    
    created_at    = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.id} by {self.customer_name}"

    # NOTE: Untuk list order, gunakan annotate() di view agar tidak N+1:
    # Order.objects.annotate(total_price=Sum(F('items__quantity') * F('items__price')))
    @property
    def total_price(self):
        return self.items.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total'] or 0

    class Meta:
        db_table = 'lumra_config_orders'


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    variant  = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price    = models.DecimalField(max_digits=12, decimal_places=2)  # harga saat transaksi
    
    # 🟢 FIELD EXTENSIONS (16 Apr 2026)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Harga cost/modal')
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Diskon nominal')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Diskon persen')
    batch_id = models.ForeignKey('ProductBatches', null=True, blank=True, on_delete=models.SET_NULL, help_text='Batch/lot produk')
    notes    = models.TextField(blank=True, help_text='Catatan item')

    def __str__(self):
        return f"{self.variant.sku} x {self.quantity}"

    class Meta:
        db_table = 'lumra_config_orderitems'


# =========================
# PRODUCTDETAIL (DATABASE VIEW)
# =========================

class ProductDetail(models.Model):
    sku         = models.CharField(max_length=50, primary_key=True)
    name        = models.CharField(max_length=100)
    price_buy   = models.DecimalField(max_digits=12, decimal_places=2)
    price_sell  = models.DecimalField(max_digits=12, decimal_places=2)
    bean_type   = models.CharField(max_length=100, null=True)
    tag         = models.CharField(max_length=100, null=True)
    roast_level = models.CharField(max_length=100, null=True)
    processing  = models.CharField(max_length=100, null=True)
    category    = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)

    class Meta:
        managed  = False
        db_table = 'product_details_view'


# =========================
# STOCK OPNAME WORKFLOW
# =========================

class StockOpnameSession(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted',   'Submitted for Approval'),
        ('approved',    'Approved & Applied'),
        ('rejected',    'Rejected'),
    ]

    location   = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='opname_sessions')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='opname_sessions')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at  = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Opname {self.id} - {self.location.name} ({self.status})"

    class Meta:
        db_table = 'lumra_config_stockopname_session'
        ordering = ['-created_at']


class StockOpnameItem(models.Model):
    session     = models.ForeignKey(StockOpnameSession, on_delete=models.CASCADE, related_name='items')
    variant     = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    current_stock = models.IntegerField(default=0)
    counted_qty   = models.IntegerField()
    notes         = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    @property
    def difference(self):
        return self.counted_qty - self.current_stock

    @property
    def is_accurate(self):
        return self.difference == 0

    def __str__(self):
        return f"{self.variant.sku} - Session {self.session.id}"

    class Meta:
        db_table        = 'lumra_config_stockopname_item'
        unique_together = ('session', 'variant')
        ordering        = ['variant__sku']


# =========================
# PRODUCTION & RECIPE MODELS
# =========================

class RecipeCategory(models.Model):
    """
    Kategori khusus untuk Recipe — terpisah dari Category umum
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    agar tidak bercampur dengan kategori produk/inventory.
    """
    name        = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    is_active   = models.BooleanField(default=True)
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    created_at  = models.DateTimeField(auto_now_add=True)
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table           = 'production_recipe_categories'
        verbose_name       = 'Recipe Category'
        verbose_name_plural = 'Recipe Categories'
        ordering           = ['name']


class Recipe(models.Model):
    name             = models.CharField(max_length=255, unique=True)
    description      = models.TextField(blank=True)
    instructions     = models.TextField(blank=True)

    # ForeignKey ke RecipeCategory, bukan Category umum
    category         = models.ForeignKey(
        RecipeCategory,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='recipes',
    )

    yield_quantity   = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    yield_unit       = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    preparation_time = models.IntegerField(default=5)

    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # Stored cost fields — dihitung ulang via recalculate_cost(), BUKAN di save()
    # agar terhindar dari infinite loop saat RecipeIngredient.save() trigger Recipe.save()
    total_cost    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_archived = models.BooleanField(default=False)
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    created_at  = models.DateTimeField(auto_now_add=True)
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function atau template partial
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    # ------------------------------------------------------------------
    # PERBAIKAN: Pisahkan kalkulasi cost dari save() biasa.
    #
    # Masalah sebelumnya:
    #   RecipeIngredient.save()
    #     → recipe.save()           ← trigger calculate_cost
    #       → self.ingredients.all() ← akses DB saat object belum selesai commit
    #         → [jika ada signal/override lain] bisa loop tak terbatas
    #
    # Solusi: Recipe.save() TIDAK memanggil calculate_cost() secara otomatis.
    # Sebagai gantinya, gunakan recalculate_cost() secara eksplisit dari:
    #   1. RecipeIngredient.save() dan .delete() (setelah super())
    #   2. View setelah formset.save()
    # ------------------------------------------------------------------
    def recalculate_cost(self):
        """
        Hitung ulang total_cost dan cost_per_unit dari semua ingredient,
        lalu simpan HANYA field tersebut (update_fields) untuk menghindari
        recursive save() chain.
        """
        ingredients = self.ingredients.all()
        total = sum(ing.subtotal_cost for ing in ingredients)
        self.total_cost = total
        self.cost_per_unit = (
            total / self.yield_quantity
            if self.yield_quantity and self.yield_quantity > 0
            else 0
        )
        # update_fields mencegah seluruh model di-save ulang
        # dan menghindari infinite loop
        Recipe.objects.filter(pk=self.pk).update(
            total_cost=self.total_cost,
            cost_per_unit=self.cost_per_unit,
        )

    @property
    def ingredient_count(self):
        """
        Hindari memanggil property ini dalam loop list.
        Gunakan annotate() di view:
          Recipe.objects.annotate(ingredient_count=Count('ingredients'))
        """
        return self.ingredients.count()

    class Meta:
        db_table = 'production_recipes'
        ordering = ['name']


class RecipeIngredient(models.Model):
    recipe  = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)

    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit     = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)

    # Stored cost — di-snapshot saat save agar history harga tetap akurat
    # meski price_buy ProductVariant berubah di kemudian hari
    unit_cost     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipe.name} - {self.variant.sku}"

    def save(self, *args, **kwargs):
        # Snapshot harga beli saat ini sebagai unit_cost
        self.unit_cost    = self.variant.price_buy
        self.subtotal_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)
        # Trigger recalculate via update_fields — TIDAK memanggil recipe.save()
        # sehingga tidak ada infinite loop
        self.recipe.recalculate_cost()

    def delete(self, *args, **kwargs):
        recipe = self.recipe
        super().delete(*args, **kwargs)
        # Trigger recalculate setelah ingredient dihapus
        recipe.recalculate_cost()

    class Meta:
        db_table        = 'production_recipe_ingredients'
        unique_together = ('recipe', 'variant')
        ordering        = ['variant__sku']


# =========================
# SUPPLIER PRICING MODELS
# =========================

class SupplierPrice(models.Model):
    vendor   = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='supplier_prices')
    variant  = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='supplier_prices')

    unit_price       = models.DecimalField(max_digits=12, decimal_places=2)
    currency         = models.CharField(max_length=3, default='IDR')
    minimum_quantity = models.IntegerField(default=1)
    maximum_quantity = models.IntegerField(null=True, blank=True)
    lead_time_days   = models.IntegerField(default=0)

    is_active    = models.BooleanField(default=True)
    is_preferred = models.BooleanField(default=False)

    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    effective_date  = models.DateField(null=True, blank=True)
    valid_until     = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.variant.sku} @ {self.unit_price}"

    class Meta:
        db_table        = 'lumra_config_supplier_prices'
        unique_together = ('vendor', 'variant')
        ordering        = ['-is_preferred', 'unit_price']


# =========================
# ACCOUNTING MODELS
# =========================

class Account(models.Model):
    ACCOUNT_TYPES = [
        ("asset", "Asset"),
        ("liability", "Liability"),
        ("equity", "Equity"),
        ("revenue", "Revenue"),
        ("expense", "Expense"),
    ]

    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, db_index=True)
    level = models.PositiveSmallIntegerField(default=2)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    is_active = models.BooleanField(default=True)
    allow_posting = models.BooleanField(default=True)
    is_cash_account = models.BooleanField(default=False)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounting_accounts"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def normal_side(self):
        return "debit" if self.account_type in {"asset", "expense"} else "credit"

    def clean(self):
        if self.level == 1:
            self.allow_posting = False
        if self.parent and self.parent_id == self.pk:
            raise ValidationError("Parent account tidak boleh sama dengan akun ini.")
        if self.parent and self.parent.account_type != self.account_type:
            raise ValidationError("Parent account harus memiliki tipe akun yang sama.")


class JournalEntry(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("posted", "Posted"),
    ]

    SOURCE_CHOICES = [
        ("manual", "Manual"),
        ("payment_voucher", "Payment Voucher"),
        ("system", "System"),
    ]

    number = models.CharField(max_length=30, unique=True, db_index=True)
    date = models.DateField(default=timezone.localdate, db_index=True)
    reference = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True)
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default="manual")
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_journal_entries")
    posted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="posted_journal_entries")
    posted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounting_journal_entries"
        ordering = ["-date", "-id"]

    def __str__(self):
        return self.number

    @property
    def total_debit(self):
        return self.lines.aggregate(total=Sum("debit"))["total"] or Decimal("0")

    @property
    def total_credit(self):
        return self.lines.aggregate(total=Sum("credit"))["total"] or Decimal("0")

    @property
    def total_amount(self):
        return self.total_debit

    @property
    def is_balanced(self):
        return self.total_debit == self.total_credit and self.total_debit > 0

    def clean(self):
        if self.pk and not self.is_balanced:
            raise ValidationError("Journal entry harus seimbang antara debit dan kredit.")


class JournalEntryLine(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="lines")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="journal_lines")
    description = models.CharField(max_length=255, blank=True)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounting_journal_entry_lines"
        ordering = ["id"]

    def __str__(self):
        return f"{self.journal_entry.number} - {self.account.code}"

    def clean(self):
        if self.debit and self.credit:
            raise ValidationError("Satu baris jurnal hanya boleh debit atau kredit.")
        if not self.debit and not self.credit:
            raise ValidationError("Baris jurnal harus memiliki nilai debit atau kredit.")
        if self.account and not self.account.allow_posting:
            raise ValidationError("Akun header tidak boleh dipakai untuk posting.")


class AccountsPayableEntry(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("partial", "Partial"),
        ("paid", "Paid"),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="payables")
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    invoice_date = models.DateField(db_index=True)
    due_date = models.DateField(db_index=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open", db_index=True)
    memo = models.CharField(max_length=255, blank=True)
    journal_entry = models.ForeignKey(JournalEntry, null=True, blank=True, on_delete=models.SET_NULL, related_name="ap_entries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounting_accounts_payable"
        ordering = ["due_date", "vendor__name"]

    def __str__(self):
        return f"{self.invoice_number} - {self.vendor.name}"

    @property
    def balance(self):
        return max(self.total_amount - self.paid_amount, Decimal("0"))


class AccountsReceivableEntry(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("partial", "Partial"),
        ("paid", "Paid"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="receivables")
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    invoice_date = models.DateField(db_index=True)
    due_date = models.DateField(db_index=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open", db_index=True)
    memo = models.CharField(max_length=255, blank=True)
    journal_entry = models.ForeignKey(JournalEntry, null=True, blank=True, on_delete=models.SET_NULL, related_name="ar_entries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounting_accounts_receivable"
        ordering = ["due_date", "customer__name"]

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name}"

    @property
    def balance(self):
        return max(self.total_amount - self.paid_amount, Decimal("0"))


class PaymentVoucher(models.Model):
    METHOD_CHOICES = [
        ("transfer", "Transfer"),
        ("check", "Cek/Giro"),
        ("cash", "Tunai"),
    ]

    number = models.CharField(max_length=30, unique=True, db_index=True)
    date = models.DateField(default=timezone.localdate, db_index=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="payment_vouchers")
    cash_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="payment_vouchers")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="transfer")
    memo = models.CharField(max_length=255, blank=True)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="payment_vouchers")
    journal_entry = models.OneToOneField(JournalEntry, null=True, blank=True, on_delete=models.SET_NULL, related_name="payment_voucher")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounting_payment_vouchers"
        ordering = ["-date", "-id"]

    def __str__(self):
        return self.number


class PaymentVoucherAllocation(models.Model):
    voucher = models.ForeignKey(PaymentVoucher, on_delete=models.CASCADE, related_name="allocations")
    payable_entry = models.ForeignKey(AccountsPayableEntry, on_delete=models.PROTECT, related_name="voucher_allocations")
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        db_table = "accounting_payment_voucher_allocations"
        ordering = ["id"]

    def __str__(self):
        return f"{self.voucher.number} - {self.payable_entry.invoice_number}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Nominal alokasi harus lebih besar dari nol.")
        if self.payable_entry_id and self.amount > self.payable_entry.balance:
            raise ValidationError("Nominal alokasi melebihi sisa hutang invoice.")

class SalesTarget(models.Model):
    """
    Target revenue bulanan yang bisa diset oleh admin.
    Satu record per bulan per tahun.
    """
    MONTH_CHOICES = [
        (1,'Januari'),(2,'Februari'),(3,'Maret'),(4,'April'),
        (5,'Mei'),(6,'Juni'),(7,'Juli'),(8,'Agustus'),
        (9,'September'),(10,'Oktober'),(11,'November'),(12,'Desember'),
    ]
 
    year         = models.IntegerField(verbose_name='Tahun')
    month        = models.IntegerField(choices=MONTH_CHOICES, verbose_name='Bulan')
    target_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name='Target Revenue (Rp)'
    )
    notes        = models.TextField(blank=True, verbose_name='Catatan')
    created_by   = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sales_targets'
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table        = 'lumra_config_sales_targets'
        unique_together = ('year', 'month')
        ordering        = ['-year', '-month']
        verbose_name    = 'Sales Target'
 
    def __str__(self):
        return f"Target {self.get_month_display()} {self.year}: Rp {self.target_amount:,.0f}"
 
    @property
    def target_daily(self):
        """Estimasi target harian (dibagi 26 hari kerja)."""
        return self.target_amount / 26


# =========================
# WAREHOUSE / LOGISTICS MODELS
# =========================

class WarehouseZone(models.Model):
    ZONE_TYPES = [
        ("rack", "Rack"),
        ("bulk", "Bulk"),
        ("staging", "Staging"),
        ("cold", "Cold Storage"),
        ("frozen", "Frozen"),
        ("other", "Other"),
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="zones")
    code     = models.CharField(max_length=30)
    name     = models.CharField(max_length=120)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPES, default="rack")
    capacity  = models.PositiveIntegerField(default=0, help_text="Capacity in unit/pcs (simple).")
    is_active = models.BooleanField(default=True)
    notes     = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lumra_config_warehouse_zones"
        unique_together = ("location", "code")
        ordering = ["location__name", "code"]

    def __str__(self):
        return f"{self.location.name} - {self.code}"


class InventoryBatch(models.Model):
    """
    Simple batch/lot tracking per variant + location.
    Note: Stock in Lumra is a ledger (Stock model). This table is a UI-friendly
    register; quantity_on_hand is intentionally simple for now.
    """

    variant   = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="batches")
    location  = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="batches")
    zone      = models.ForeignKey(WarehouseZone, on_delete=models.SET_NULL, null=True, blank=True, related_name="batches")

    code      = models.CharField(max_length=50, db_index=True)
    quantity_on_hand = models.PositiveIntegerField(default=0)

    production_date = models.DateField(null=True, blank=True)
    expiry_date     = models.DateField(null=True, blank=True, db_index=True)
    notes           = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_batches")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lumra_config_inventory_batches"
        unique_together = ("location", "code")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} - {self.variant.sku}"


class StockAdjustmentReason(models.Model):
    code        = models.CharField(max_length=30, unique=True)
    name        = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lumra_config_stock_adjustment_reasons"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


# =========================
# PRODUCTION MODELS (BOM + Orders)
# =========================

class BillOfMaterial(models.Model):
    finished_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="boms",
        help_text="The produced/finished SKU.",
    )
    code       = models.CharField(max_length=50, unique=True, db_index=True)
    version    = models.PositiveIntegerField(default=1)
    name       = models.CharField(max_length=255, blank=True)
    is_active  = models.BooleanField(default=True)
    notes      = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_boms")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "production_bill_of_materials"
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["finished_variant", "is_active"])]

    def __str__(self):
        return self.code


class BillOfMaterialItem(models.Model):
    bom       = models.ForeignKey(BillOfMaterial, on_delete=models.CASCADE, related_name="items")
    component = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="bom_components")
    quantity  = models.DecimalField(max_digits=12, decimal_places=2)
    unit      = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    notes     = models.TextField(blank=True)

    class Meta:
        db_table = "production_bom_items"
        unique_together = ("bom", "component")
        ordering = ["component__sku"]

    def __str__(self):
        return f"{self.bom.code} - {self.component.sku}"


class ProductionOrder(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("on_hold", "On Hold"),
        ("cancelled", "Cancelled"),
    ]

    code     = models.CharField(max_length=50, unique=True, db_index=True)
    bom      = models.ForeignKey(BillOfMaterial, on_delete=models.PROTECT, related_name="production_orders")
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    target_quantity   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    produced_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit              = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)

    scheduled_date = models.DateField(null=True, blank=True, db_index=True)
    started_at     = models.DateTimeField(null=True, blank=True)
    completed_at   = models.DateTimeField(null=True, blank=True)
    priority       = models.CharField(max_length=20, default="Normal")
    line           = models.CharField(max_length=80, blank=True)
    notes          = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_production_orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "production_orders"
        ordering = ["-created_at"]

    def __str__(self):
        return self.code


class ProductionMaterialConsumption(models.Model):
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name="consumptions")
    component        = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="consumptions")
    quantity         = models.DecimalField(max_digits=12, decimal_places=2)
    unit             = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    consumed_at      = models.DateTimeField(default=timezone.now, db_index=True)
    notes            = models.TextField(blank=True)

    class Meta:
        db_table = "production_material_consumptions"
        ordering = ["-consumed_at"]

    def __str__(self):
        return f"{self.production_order.code} - {self.component.sku}"


class FinishedGoodsReceipt(models.Model):
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name="receipts")
    finished_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="finished_receipts")
    location         = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="finished_receipts")
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2)
    received_at      = models.DateTimeField(default=timezone.now, db_index=True)
    notes            = models.TextField(blank=True)

    class Meta:
        db_table = "production_finished_goods_receipts"
        ordering = ["-received_at"]

    def __str__(self):
        return f"{self.production_order.code} receipt"


class ProductionWasteRecord(models.Model):
    WASTE_TYPES = [
        ("scrap", "Scrap"),
        ("spoilage", "Spoilage"),
        ("rework", "Rework"),
        ("other", "Other"),
    ]

    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name="wastes")
    component        = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True, related_name="waste_records")
    waste_type       = models.CharField(max_length=20, choices=WASTE_TYPES, default="scrap")
    quantity         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit             = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_at      = models.DateTimeField(default=timezone.now, db_index=True)
    notes            = models.TextField(blank=True)

    class Meta:
        db_table = "production_waste_records"
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.production_order.code} waste"


# =========================
# 5 CRITICAL MODELS UNTUK BUSINESS OPERATIONS
# =========================

class StockMovement(models.Model):
    """
    🔴 CRITICAL Model untuk audit trail semua pergerakan stok.
    Setiap perubahan stok (pembelian, penjualan, produksi, retur, transfer, adjustment)
    di-track di sini.
    """
    
    MOVEMENT_TYPES = [
        ('purchase_in', 'Pembelian Masuk'),
        ('sales_out', 'Penjualan Keluar'),
        ('production_in', 'Produksi Selesai'),
        ('production_out', 'Konsumsi Produksi'),
        ('retur_in', 'Retur Masuk'),
        ('transfer_in', 'Transfer Masuk'),
        ('transfer_out', 'Transfer Keluar'),
        ('adjustment_in', 'Penyesuaian Masuk'),
        ('adjustment_out', 'Penyesuaian Keluar'),
    ]
    
    product = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name='stock_movements')
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES, db_index=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Reference ke dokumen yang membuat movement ini
    reference_type = models.CharField(max_length=50, blank=True, help_text="Tipe dokumen: 'order', 'requisition', 'production', 'retur', etc")
    reference_id = models.PositiveIntegerField(null=True, blank=True, help_text="ID dari dokumen referensi")
    reference_number = models.CharField(max_length=100, blank=True, help_text="Nomor dokumen: INV-001, PO-001, etc")
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='stock_movements_created')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lumra_config_stockmovement'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'location', 'created_at']),
            models.Index(fields=['movement_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.sku} ({self.quantity})"


class Returns(models.Model):
    """
    🔴 CRITICAL Header model untuk retur/refund dari customer.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    order = models.ForeignKey('Order', on_delete=models.PROTECT, related_name='returns')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='returns')
    retur_number = models.CharField(max_length=50, unique=True, db_index=True)
    retur_date = models.DateField(default=timezone.localdate, db_index=True)
    
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    reason = models.TextField()
    notes = models.TextField(blank=True)
    
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='returns_approved')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='returns_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lumra_config_returns'
        ordering = ['-retur_date']
        indexes = [
            models.Index(fields=['status', 'retur_date']),
        ]

    def __str__(self):
        return f"{self.retur_number}"


class ReturnItems(models.Model):
    """
    🔴 CRITICAL Detail item yang di-retur dari pelanggan.
    """
    
    RETURN_REASONS = [
        ('defective', 'Produk Cacat'),
        ('wrong_item', 'Item Salah'),
        ('quality_issue', 'Masalah Kualitas'),
        ('customer_request', 'Permohonan Pelanggan'),
        ('expired', 'Produk Kadaluarsa'),
        ('other', 'Lainnya'),
    ]
    
    retur_header = models.ForeignKey(Returns, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=20, choices=RETURN_REASONS, default='customer_request')
    
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lumra_config_returnitems'
        ordering = ['id']

    def __str__(self):
        return f"{self.product.sku} x{self.quantity}"


class Payments(models.Model):
    """
    🔴 CRITICAL Pencatatan pembayaran untuk Order.
    Support split payment (multiple payment methods dalam satu order).
    """
    
    PAYMENT_METHODS = [
        ('cash', 'Tunai'),
        ('debit_card', 'Kartu Debit'),
        ('credit_card', 'Kartu Kredit'),
        ('qris', 'QRIS'),
        ('bank_transfer', 'Transfer Bank'),
        ('check', 'Cek'),
        ('other', 'Lainnya'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    order = models.ForeignKey('Order', on_delete=models.PROTECT, related_name='payments')
    payment_number = models.CharField(max_length=50, unique=True, db_index=True)
    payment_date = models.DateField(default=timezone.localdate, db_index=True)
    
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending', db_index=True)
    
    # Reference untuk bank transfer, check number, etc
    reference_number = models.CharField(max_length=100, blank=True)
    reference_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    received_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='payments_received')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lumra_config_payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['order', 'payment_date']),
            models.Index(fields=['status', 'payment_date']),
        ]

    def __str__(self):
        return f"{self.payment_number} - {self.amount}"


class ProductBatches(models.Model):
    """
    🔴 CRITICAL Model untuk tracking batch & expiry date produk.
    Sangat penting untuk:
    - Tracking expiry dates
    - Batch traceability
    - FIFO (First In First Out) inventory management
    """
    
    product = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name='expiry_batches')
    batch_number = models.CharField(max_length=100, db_index=True, help_text="Nomor batch/lot dari supplier atau produksi")
    
    manufacturing_date = models.DateField(help_text="Tanggal produksi/manufacturing")
    expiry_date = models.DateField(db_index=True, help_text="Tanggal kadaluarsa produk")
    
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='product_batches')
    quantity_in = models.DecimalField(max_digits=12, decimal_places=2, help_text="Qty batch yang masuk")
    quantity_available = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Qty yang masih tersedia")
    
    # Metadata
    supplier_batch_number = models.CharField(max_length=100, blank=True)
    supplier = models.ForeignKey(Vendor, null=True, blank=True, on_delete=models.SET_NULL, related_name='product_batches')
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lumra_config_product_batches'
        ordering = ['expiry_date']
        indexes = [
            models.Index(fields=['product', 'location']),
            models.Index(fields=['expiry_date', 'quantity_available']),
        ]
        unique_together = [['product', 'batch_number', 'location']]

    def __str__(self):
        return f"{self.product.sku} - Batch {self.batch_number} (Exp: {self.expiry_date})"
    
    @property
    def is_expired(self):
        """Cek apakah batch ini sudah expired"""
        from datetime import date
        return self.expiry_date <= date.today()
    
    @property
    def days_until_expiry(self):
        """Berapa hari lagi sampai expired"""
        from datetime import date
        diff = (self.expiry_date - date.today()).days
        return max(diff, 0)  # Return 0 jika sudah expired

