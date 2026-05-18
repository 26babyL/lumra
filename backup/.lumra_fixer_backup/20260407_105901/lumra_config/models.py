# your_app/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.utils import timezone
from django.core.exceptions import ValidationError

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
        db_table = '_categories'


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
        db_table = '_vendors'


class Tax(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    rate        = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.rate * 100}%)"

    class Meta:
        db_table = '_taxes'


class Unit(models.Model):
    name        = models.CharField(max_length=50, unique=True)
    symbol      = models.CharField(max_length=10, blank=True)  # renamed from short_name → symbol (konsisten dengan template)
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = '_units'


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
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    unit        = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
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
    last_updated     = models.DateTimeField(auto_now=True)
    created_at       = models.DateTimeField(auto_now_add=True)

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

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'lumra_config_userprofile'


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

    name             = models.CharField(max_length=255, db_index=True)
    email            = models.EmailField(unique=True, db_index=True)
    phone            = models.CharField(max_length=20, blank=True)
    address          = models.TextField(blank=True)
    city             = models.CharField(max_length=100, blank=True)
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
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer      = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=100)  # kept for backward compatibility
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
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
    # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
    variant  = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price    = models.DecimalField(max_digits=12, decimal_places=2)  # harga saat transaksi

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
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
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
    created_at  = models.DateTimeField(auto_now_add=True)
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