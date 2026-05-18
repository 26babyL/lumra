# 🚀 LUMRA ERP - Database Quick Reference Card
**Essential Commands & Model Guide for Developers**  
*Keep this handy while coding!*

---

## 🔥 Most Important Commands

```bash
# Check database connection
python manage.py dbshell

# Create migrations
python manage.py makemigrations lumra_config

# Apply migrations
python manage.py migrate lumra_config

# Show migration status
python manage.py showmigrations lumra_config

# Start Django shell
python manage.py shell

# Check for issues
python manage.py check

# Create superuser
python manage.py createsuperuser

# Start dev server
python manage.py runserver

# Reset migrations (CAREFUL!)
python manage.py migrate lumra_config zero
```

---

## 🎯 Common Django Shell Operations

```python
# Import all models
python manage.py shell
>>> from lumra_config.models import *

# Create master data
>>> category = Category.objects.create(name='Beverages', code='BEV')
>>> vendor = Vendor.objects.create(name='Local Supplier', code='LOCAL')
>>> unit = Unit.objects.create(name='Liter', symbol='L')
>>> tax = Tax.objects.create(name='VAT', rate=10.00)
>>> location = Location.objects.create(name='Warehouse A')

# Create product
>>> product = Product.objects.create(
...     name='Coffee Arabica',
...     sku='COFFEE001',
...     category=category,
...     vendor=vendor,
...     unit=unit,
...     tax=tax,
...     description='Premium quality'
... )

# Create variant
>>> variant = ProductVariant.objects.create(
...     product=product,
...     sku='COFFEE001-1KG',
...     price_buy=50000,
...     price_sell=75000,
...     weight=1.0
... )

# Create stock
>>> stock = Stock.objects.create(
...     variant=variant,
...     location=location,
...     quantity=100,
...     transaction_type='in'
... )

# Check relationships
>>> product.category.name
>>> variant.product.name
>>> stock.variant.product.name
>>> product.variants.all().count()

# Query operations
>>> Product.objects.filter(category=category)
>>> ProductVariant.objects.filter(price_sell__gt=100000)
>>> Stock.objects.filter(location=location).aggregate(Sum('quantity'))

# Update data
>>> product.description = 'Updated description'
>>> product.save()

# Delete with cascade
>>> product.delete()  # Deletes product AND all variants & stocks

# Count records
>>> Product.objects.count()
>>> Category.objects.count()
```

---

## 📋 Model Reference - Quick Lookup

### Master Data Models

#### Category
```python
Category.objects.create(
    name='Category Name',          # Required
    code='CAT',                    # Required, Unique
    parent=parent_category,        # Optional, for hierarchy
    description='Details'          # Optional
)
# Usage: Organize products (Beverages > HotDrinks > Coffee)
# Unique: name + code
```

#### Unit
```python
Unit.objects.create(
    name='Kilogram',               # Required
    symbol='kg',                   # Required
    description='Weight measure'   # Optional
)
# Usage: Product measurement (kg, L, pcs, box)
# Unique: name, symbol
```

#### Vendor
```python
Vendor.objects.create(
    name='Supplier Name',          # Required
    code='SUPP001',                # Required, Unique
    contact_person='John'          # Optional
)
# Usage: Link to products (who supplies this product)
# Unique: name, code
```

#### Tax
```python
Tax.objects.create(
    name='VAT',                    # Required, Unique
    rate=10.00                     # Required (0-100%)
)
# Usage: Applied to product prices
# Unique: name
```

#### Location
```python
Location.objects.create(
    name='Warehouse A',            # Required, Unique
    code='WH_A',                   # Required, Unique
    address='123 Main St'          # Optional
)
# Usage: Storage locations for stock
# Unique: name, code
```

#### Customer
```python
Customer.objects.create(
    name='Customer Name',          # Required
    phone='08123456789',           # Indexed
    email='customer@email.com',    # Unique
    address='123 Street',
    city='Jakarta'
)
# Usage: Sales, Orders, Invoicing
# Unique: email
# Indexed: phone
```

---

### Product Models

#### Product
```python
Product.objects.create(
    name='Product Name',           # Required, Unique
    sku='SKU123',                  # Required, Indexed, Unique
    category=category,             # Required FK
    vendor=vendor,                 # Required FK
    unit=unit,                     # Required FK
    tax=tax,                       # Required FK
    description='Details',         # Optional
    is_active=True                 # Default: True
)
# Properties: variants (list), total_stock (aggregate)
# FK Cascade: Deleting category DOES NOT delete product (PROTECT)
# Unique: name, sku
# Indexed: sku, category, is_active
```

#### ProductVariant
```python
ProductVariant.objects.create(
    product=product,               # Required FK (CASCADE)
    sku='COFFEE-1KG',              # Required, Unique
    price_buy=50000,               # Required
    price_sell=75000,              # Required
    weight=1.0,                    # Optional
    length=10.0,                   # Optional
    width=10.0,                    # Optional
    height=10.0,                   # Optional
    is_active=True                 # Default: True
)
# Properties: total_stock (aggregate), margin (calculated)
# FK Cascade: Deleting product DELETES all variants (CASCADE)
# Unique: sku
# Indexes: (product, is_active), sku
```

#### ProductAttribute
```python
ProductAttribute.objects.create(
    variant=variant,               # Required FK (CASCADE)
    attribute_name='Color',        # Required
    attribute_value='Brown'        # Required
)
# Usage: Color: Brown, Size: Large, Brand: Premium, etc
# FK Cascade: Deleting variant DELETES all attributes (CASCADE)
# No unique constraint (multiple attributes per variant)
```

---

### Stock Management Models

#### Stock
```python
Stock.objects.create(
    variant=variant,               # Required FK (CASCADE)
    location=location,             # Required FK (CASCADE)
    quantity=100,                  # Required
    transaction_type='in',         # Required (audit log)
    notes='Initial stock'          # Optional
)
# Constraint: UNIQUE (variant, location) - one stock per product per location
# FK Cascade: Both cascade delete
# Properties: value (quantity × price), available_quantity
# Common queries:
#   - Stock per location: Stock.objects.filter(location=loc)
#   - Total variant stock: Stock.objects.filter(variant=var).aggregate(Sum('quantity'))
```

#### StockOpnameSession
```python
StockOpnameSession.objects.create(
    location=location,             # Required FK (CASCADE)
    start_date=datetime.now(),     # Required
    status='in_progress',          # Required choice
    created_by=user                # Required FK (SET_NULL)
)
# Status choices:
#   - 'in_progress': Currently being counted
#   - 'completed': Counting finished
#   - 'verified': Verified against system
# FK user CASCADE -> SET_NULL: Deleting user clears this field
# Reverse: session.opname_items (all items counted)
```

#### StockOpnameItem
```python
StockOpnameItem.objects.create(
    session=opname_session,        # Required FK (CASCADE)
    variant=variant,               # Required FK (SET_NULL)
    location=location,             # Required FK (SET_NULL)
    physical_count=95,             # Required (what was counted)
    system_count=100,              # Required (what system has)
    difference=-5                  # Calculated (physical - system)
)
# Calculation: Auto-calculate difference = physical_count - system_count
# FK Cascade: Deleting session deletes all items (CASCADE)
# FK variants: Can be NULL if variant was deleted but count still kept
```

---

### Workflow Models

#### Requisition
```python
Requisition.objects.create(
    number='REQ-2026-001',          # Required, Unique
    location_from=location1,        # Required FK (SET_NULL)
    location_to=location2,          # Required FK (SET_NULL)
    status='waiting',               # Required choice
    requested_by=user,              # Required FK (SET_NULL)
    approved_by=None,               # Optional FK (SET_NULL)
    created_date=datetime.now()     # Auto
)
# Status workflow:
#   waiting → approved → in_transit → completed (or rejected)
# Reverse: requisition.items (all items requested)
# Key fields: requested_by, approved_by (NULLABLE - user can be deleted)
```

#### RequisitionItem
```python
RequisitionItem.objects.create(
    requisition=requisition,       # Required FK (CASCADE)
    variant=variant,               # Required FK (SET_NULL)
    quantity_required=50,          # Required
    quantity_received=0,           # Default: 0, updated when delivered
    status='pending'               # Required choice
)
# Status: pending → received → rejected
# FK variant: Can be NULL if product deleted but requisition kept
# Calculation: quantity_received can be less than required
```

#### Transfer
```python
Transfer.objects.create(
    number='TRF-2026-001',          # Required, Unique
    location_from=warehouse_a,      # Required FK (SET_NULL)
    location_to=warehouse_b,        # Required FK (SET_NULL)
    status='in_transit',            # Required choice
    created_by=user,                # Required FK (SET_NULL)
    created_date=datetime.now()     # Auto
)
# Status: in_transit → completed (or rejected)
# Similar to Requisition but for system-initiated moves
# Reverse: transfer.items (all items being transferred)
```

#### TransferItem
```python
TransferItem.objects.create(
    transfer=transfer,             # Required FK (CASCADE)
    variant=variant,               # Required FK (SET_NULL)
    quantity=50,                   # Required
    quantity_received=0,           # Default: 0
    status='in_transit'            # Required choice
)
# Similar to RequisitionItem
# Tracks individual products moving between locations
```

---

### Sales Models

#### Order
```python
Order.objects.create(
    number='ORD-2026-001',          # Required, Unique
    customer=customer,              # Required FK (SET_NULL)
    order_date=datetime.now(),      # Required, Auto
    status='pending',               # Required choice
    total_amount=750000,            # Required
    created_by=user                 # Required FK (SET_NULL)
)
# Status: pending → confirmed → shipped → delivered (or cancelled)
# total_amount: CALCULATED from order items (DO NOT manually set)
# Reverse: order.items (all products in this order)
```

#### OrderItem
```python
OrderItem.objects.create(
    order=order,                   # Required FK (CASCADE)
    variant=variant,               # Required FK (SET_NULL)
    quantity=10,                   # Required
    price=50000,                   # SNAPSHOT (price at time of order, not current)
    subtotal=500000                # CALCULATED (quantity × price)
)
# IMPORTANT: price field stores price AT ORDER TIME
#            Do NOT recalculate from current ProductVariant.price_sell
# Calculation: subtotal = quantity × price (automatic)
# FK variant: Can be NULL if product deleted but order kept (audit trail)
```

---

### Production/Recipe Models

#### RecipeCategory
```python
RecipeCategory.objects.create(
    name='Drinks Category',        # Required, Unique
    code='DRINKCAT',               # Required, Unique
    description='All drinks'       # Optional
)
# Usage: Organize recipes (Beverages, Main Courses, etc)
```

#### Recipe
```python
Recipe.objects.create(
    name='Coffee Latte',           # Required, Unique
    code='RECIPE01',               # Required, Unique
    category=recipe_category,      # Required FK (PROTECT)
    yield_quantity=1,              # Required (how many units produced)
    total_cost=0,                  # CALCULATED (sum of ingredients cost)
    cost_per_unit=0,               # CALCULATED (total_cost / yield_quantity)
    is_active=True                 # Default: True
)
# Calculations: Trigger via RecipeIngredient.save()
# IMPORTANT: Uses update_fields to avoid infinite loops
# Reverse: recipe.ingredients (all ingredients in recipe)
# Process: Add recipe → Add ingredients → Cost auto-calculated
```

#### RecipeIngredient
```python
RecipeIngredient.objects.create(
    recipe=recipe,                 # Required FK (CASCADE)
    variant=variant,               # Required FK (SET_NULL)
    quantity=1,                    # Required (1 shot of espresso)
    unit_cost=10000,               # SNAPSHOT (saved at creation)
    subtotal_cost=10000            # CALCULATED (quantity × unit_cost)
)
# IMPORTANT: When saved, triggers recipe.recalculate_cost()
#            This recalculates parent recipe total_cost
# SNAPSHOT: unit_cost captured from variant.price_buy at creation time
#           NOT linked to current variant price (for historical accuracy)
# Reverse: recipe.ingredients manager
# Save trigger: Automatically updates parent Recipe.total_cost
```

#### SupplierPrice
```python
SupplierPrice.objects.create(
    variant=variant,               # Required FK (CASCADE)
    vendor=vendor,                 # Required FK (CASCADE)
    price=45000,                   # Required (bulk price $45000)
    effective_date=datetime.now()  # Required
)
# Usage: Track historical supplier prices
# Shows how much this vendor charged for variant at this date
# CASCADE both: If variant deleted, all supplier prices gone
#              If vendor deleted, all their prices gone
# Indexes: (variant, vendor, effective_date)
```

---

### User & Analytics Models

#### UserProfile
```python
UserProfile.objects.create(
    user=django_user,              # Required OneToOne FK (CASCADE)
    phone='08123456789',           # Optional
    department='Warehouse',        # Optional
    role='Manager'                 # Optional
)
# OneToOne: Each Django user has exactly one profile
# CASCADE: Deleting user deletes profile
# Reverse: user.userprofile
# Common: user.userprofile.role to get role
```

#### SalesTarget
```python
SalesTarget.objects.create(
    year=2026,                     # Required
    month=4,                       # Required (1-12)
    target_amount=1000000000,      # Required (1 billion rupiah)
    achieved_amount=0,             # Initial: 0
    created_by=user                # Required FK (SET_NULL)
)
# Constraint: UNIQUE (year, month) - one target per month
# Calendar tracking: Year 2026, Month 4 (April 2026)
# Calculation: achieved_amount updated from orders/sales
# Updated by: Periodic batch job or manual entry
```

---

## 🔗 Key Relationships at a Glance

```
Master Data Foundation:
  Category → Products (1:M)
  Unit → Products (1:M)
  Vendor → Products (1:M)
  Tax → Products (1:M)
  Location → Stock (1:M)

Product Hierarchy:
  Product → ProductVariant (1:M, CASCADE)
  ProductVariant → ProductAttribute (1:M, CASCADE)
  ProductVariant → Stock (1:M, CASCADE)

Stock Management:
  Location → Stock (1:M, CASCADE)
  Stock ← StockOpnameSession (M:1, CASCADE)
  StockOpnameSession → StockOpnameItem (1:M, CASCADE)

Workflow:
  Location → Requisition (1:M, SET_NULL)
  User → Requisition (1:M, SET_NULL)
  Requisition → RequisitionItem (1:M, CASCADE)
  
  Location → Transfer (1:M, SET_NULL)
  User → Transfer (1:M, SET_NULL)
  Transfer → TransferItem (1:M, CASCADE)

Sales:
  Customer → Order (1:M, SET_NULL)
  Order → OrderItem (1:M, CASCADE)
  ProductVariant → OrderItem (1:M, SET_NULL)

Production:
  RecipeCategory → Recipe (1:M, PROTECT)
  Recipe → RecipeIngredient (1:M, CASCADE)
  ProductVariant → RecipeIngredient (1:M, SET_NULL)
  ProductVariant → SupplierPrice (1:M, CASCADE)
  Vendor → SupplierPrice (1:M, CASCADE)

Users:
  Django User ← UserProfile (1:1, CASCADE)
```

---

## 🎯 Optimization Tips

### Query Optimization

```python
# ✗ BAD: N+1 queries (1 + 100 queries)
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)  # 100 additional queries


# ✓ GOOD: Use select_related (1 query)
orders = Order.objects.select_related('customer').all()
for order in orders:
    print(order.customer.name)  # Already loaded


# ✗ BAD: Reverse N+1 (1 + 100 queries)
customers = Customer.objects.all()
for customer in customers:
    total = customer.order_set.all().count()


# ✓ GOOD: Use prefetch_related (2 queries)
from django.db.models import Prefetch
customers = Customer.objects.prefetch_related('order_set').all()
for customer in customers:
    total = len(customer.order_set.all())  # Already prefetched
```

### Bulk Operations

```python
# ✗ SLOW: Individual saves (100 database hits)
for i in range(100):
    Stock.objects.create(...)


# ✓ FAST: Bulk create (1-3 database hits)
stocks = [Stock(...), Stock(...), Stock(...)]
Stock.objects.bulk_create(stocks, batch_size=100)


# ✗ SLOW: Individual updates (100 hits)
for stock in stocks:
    stock.quantity = 50
    stock.save()


# ✓ FAST: Bulk update (1 hit)
Stock.objects.bulk_update(stocks, ['quantity'], batch_size=100)
```

### Aggregation

```python
# Calculate totals efficiently
from django.db.models import Sum, Count, Avg

# Total stock quantity per location
totals = Stock.objects.filter(
    location=location
).aggregate(
    total_qty=Sum('quantity'),
    variant_count=Count('variant', distinct=True)
)

# Average order value
avg_order = Order.objects.aggregate(
    avg_total=Avg('total_amount')
)
```

---

## ⚠️ Common Mistakes

```python
# ✗ WRONG: Comparing Decimal with float
if stock.quantity > 100.5:  # Danger!

# ✓ RIGHT: Use Decimal for all prices/quantities
from decimal import Decimal
if stock.quantity > Decimal('100.50'):

# ✗ WRONG: Storing price at sale from current variant
order_item.price = variant.price_sell  # Updates when variant changes

# ✓ RIGHT: Store snapshot at order time
order_item.price = variant.price_sell  # Never change after order created

# ✗ WRONG: Modifying many-to-many without save()
recipe.ingredients.add(ingredient)
# Make other changes
# User gets wrong data if exception occurs

# ✓ RIGHT: Use atomic transactions
from django.db import transaction
with transaction.atomic():
    recipe.ingredients.add(ingredient)
    recipe.save()  # Both succeed or both fail
```

---

## 📞 Quick Support Matrix

| Problem | Command | File |
|---------|---------|------|
| Check DB connection | `python manage.py dbshell` | settings.py |
| Migration stuck | `python manage.py migrate --fake-initial` | lumra_config/migrations/ |
| Can't create FK | Check parent exists first | See model FK fields |
| N+1 queries | Use `select_related()` | database reference |
| Price calculation wrong | Check decimal vs float | SupplierPrice, RecipeIngredient |
| Delete not cascading | Review FK on_delete parameter | models.py |
| Admin not showing models | Check admin.site.register() | lumra_config/admin.py |
| Query timeout | Add indexes | DATABASE_SCHEMA_MAPPING.md |

---

**🚀 Keep this card open when developing - reference it constantly!**
