# 🔗 LUMRA ERP - Database Models & Relationship Diagram
**Model-to-Model Relationship Mapping & Validation Checklist**  
*Generated: April 10, 2026*

---

## 📑 Table of Contents
1. [Model Relationship Overview](#model-relationship-overview)
2. [Models by Category](#models-by-category)
3. [Relationship Diagrams](#relationship-diagrams)
4. [Data Flow Patterns](#data-flow-patterns)
5. [Model Dependencies](#model-dependencies)
6. [Validation Checklist](#validation-checklist)
7. [Migration Strategy](#migration-strategy)
8. [Django Admin Configuration](#django-admin-configuration)

---

## 🏗️ Model Relationship Overview

### Model Statistics
```
Total Models: 32
├─ Master Data Models: 7
├─ Product Models: 4
├─ Stock Models: 4
├─ Workflow Models: 4
├─ Order Models: 2
├─ Recipe Models: 3
├─ User Models: 2
├─ Target Models: 1
└─ View Models: 1

Total Relationships: 50+
├─ OneToOne: 1
├─ ForeignKey: 46
├─ Self-referencing: 1
└─ Reverse relationships: ~30+
```

---

## 🗂️ Models by Category

### 1. Master Data Models (7 models)
Essential reference data used across system.

#### Category
```python
class Category(models.Model):
    # Fields
    name        # CharField(100) - UNIQUE, indexed
    description # TextField
    parent      # ForeignKey('self') - hierarchical
    slug        # CharField(100) - UNIQUE for URLs
    code        # CharField(10) - business code
    icon_url    # CharField(255) - category icon
    is_active   # BooleanField - soft delete
    created_at  # DateTimeField - auto timestamp
    updated_at  # DateTimeField - auto update
    
    # Relationships (reverse)
    products    # Product.category (reverse relation)
    recipes     # Recipe.category via RecipeCategory
    
    # Natural Key
    UNIQUE: name, slug
    
    # Use: Product categorization, reporting grouping
```

#### Unit
```python
class Unit(models.Model):
    # Fields
    name        # CharField(50) - UNIQUE (kg, L, pcs, etc)
    symbol      # CharField(10) - abbreviated (kg, L, p)
    description # TextField
    is_active   # BooleanField
    created_at  # DateTimeField
    
    # Relationships (reverse)
    products    # Product.unit (reverse)
    recipes     # Recipe.yield_unit (reverse)
    
    # Natural Key
    UNIQUE: name
    
    # Use: Product measurement, recipe yield
```

#### Vendor
```python
class Vendor(models.Model):
    # Fields
    name           # CharField(100) - UNIQUE, indexed
    contact_person # CharField(100) - contact name
    phone          # CharField(20) - phone number
    code           # CharField(20) - vendor code
    email          # EmailField - vendor email
    address        # TextField - vendor address
    website        # URLField - vendor website
    tax_number     # CharField(50) - tax ID
    is_active      # BooleanField
    created_at     # DateTimeField
    updated_at     # DateTimeField
    
    # Relationships (reverse)
    supplier_prices    # SupplierPrice.vendor (reverse)
    products           # Product.vendor (reverse)
    
    # Natural Key
    UNIQUE: name
    
    # Use: Supplier management, purchase orders
```

#### Tax
```python
class Tax(models.Model):
    # Fields
    name        # CharField(100) - UNIQUE (PPN, PPH, etc)
    rate        # DecimalField(5,2) - percentage (e.g., 10.00)
    description # TextField
    is_active   # BooleanField
    created_at  # DateTimeField
    
    # Relationships (reverse)
    products    # Product.tax (reverse)
    
    # Natural Key
    UNIQUE: name
    
    # Use: Tax calculation on products
```

#### Location
```python
class Location(models.Model):
    # Fields
    name          # CharField(100) - UNIQUE, indexed
    address       # TextField - physical address
    location_type # CharField(20) - 'store', 'warehouse', 'branch'
    created_at    # DateTimeField
    
    # Relationships (reverse)
    stock_entries          # Stock.location (reverse)
    requisitions_from      # Requisition.from_location (reverse)
    requisitions_to        # Requisition.to_location (reverse)
    transfers_from         # Transfer.source_location (reverse)
    transfers_to           # Transfer.destination_location (reverse)
    opname_sessions        # StockOpnameSession.location (reverse)
    user_profiles          # UserProfile.location (reverse)
    
    # Natural Key
    UNIQUE: name
    
    # Use: Multi-location warehouse management
```

#### Customer
```python
class Customer(models.Model):
    # Fields
    name             # CharField(255) - customer name
    email            # EmailField - UNIQUE, indexed
    phone            # CharField(20) - customer phone
    address          # TextField - address
    city             # CharField(100) - city
    tier             # CharField(20) - loyalty tier (bronze/silver/gold/platinum)
    loyalty_points   # IntegerField - accumulated points
    total_spent      # DecimalField(15,2) - lifetime value
    total_orders     # IntegerField - order count
    is_active        # BooleanField - soft delete
    created_at       # DateTimeField - registration date
    updated_at       # DateTimeField
    last_order_date  # DateTimeField - most recent purchase
    
    # Properties (calculated)
    average_order_value   # total_spent / total_orders
    lifetime_value        # alias for total_spent
    points                # alias for loyalty_points
    
    # Relationships (reverse)
    orders  # Order.customer (reverse)
    
    # Natural Key
    UNIQUE: email
    
    # Use: POS customer lookup, loyalty tracking, CRM
```

#### (Implied) User Profile
```python
class UserProfile(models.Model):
    # Fields
    user     # OneToOneField(User) - unique link to auth user
    location # ForeignKey(Location) - user's primary location
    
    # Use: User role/location assignment
```

---

### 2. Product Models (4 models)
Product catalog with variant support for different SKUs/sizes.

#### Product
```python
class Product(models.Model):
    # Fields
    name        # CharField(255) - product name, indexed
    description # TextField - product description
    category    # ForeignKey(Category) - product classification
    vendor      # ForeignKey(Vendor) - preferred vendor
    tax         # ForeignKey(Tax) - tax treatment
    unit        # ForeignKey(Unit) - base unit
    created_at  # DateTimeField
    updated_at  # DateTimeField
    
    # Relationships (reverse)
    variants           # ProductVariant.product (reverse) - SKUs
    
    # Use: Product master, base for variants
```

#### ProductVariant
```python
class ProductVariant(models.Model):
    # Fields
    product     # ForeignKey(Product) - parent product
    sku         # CharField(50) - UNIQUE, indexed (critical)
    size_weight # CharField(50) - package size (500g, 1L, etc)
    price_buy   # DecimalField(12,2) - cost price
    price_sell  # DecimalField(12,2) - selling price
    updated_at  # DateTimeField
    
    # Relationships (reverse)
    attributes         # ProductAttribute.variant (reverse)
    stock_entries      # Stock.variant (reverse)
    recipe_ingredients # RecipeIngredient.variant (reverse)
    order_items        # OrderItem.variant (reverse)
    supplier_prices    # SupplierPrice.variant (reverse)
    
    # Natural Key
    UNIQUE: sku
    Composite: product_id + sku
    
    # Use: Individual SKUs with pricing, stock tracking
    
    # Calculated Properties
    @property
    total_stock()      # Sum of stock across all locations
```

#### ProductAttribute
```python
class ProductAttribute(models.Model):
    # Fields
    variant    # ForeignKey(ProductVariant)
    attr_name  # CharField(100) - attribute name (roast_level, origin, bean_type)
    attr_value # CharField(255) - attribute value (medium, Indonesia, arabica)
    updated_at # DateTimeField
    
    # Use: Additional product metadata for variants
```

#### ProductDetail (View)
```python
class ProductDetail(models.Model):
    # This is a DATABASE VIEW - read-only in Django
    # Fields (denormalized from join)
    sku         # Primary key (from ProductVariant)
    name        # Product name
    price_buy   # Variant cost price
    price_sell  # Variant selling price
    bean_type   # ProductAttribute (denormalized)
    tag         # ProductAttribute (denormalized)
    roast_level # ProductAttribute (denormalized)
    processing  # ProductAttribute (denormalized)
    category    # Category name (denormalized)
    description # Product description
    
    # Use: Fast product lookup (single table query)
    # Configuration
    managed = False  # Django doesn't create/delete this table
    
    class Meta:
        db_table = 'product_details_view'
```

---

### 3. Stock Models (4 models)
Stock tracking and physical inventory management.

#### Stock
```python
class Stock(models.Model):
    # Fields
    variant          # ForeignKey(ProductVariant) - which product
    location         # ForeignKey(Location) - which location
    quantity         # IntegerField - current stock level
    transaction_type # CharField(20) - in/out/adjustment/transfer_sent/transfer_received
    notes            # TextField - transaction notes
    last_updated     # DateTimeField
    created_at       # DateTimeField
    
    # Unique Constraint
    UNIQUE: (variant_id, location_id) - only one stock record per variant per location
    
    # Use: Current stock level tracking by location
```

#### StockOpnameSession
```python
class StockOpnameSession(models.Model):
    # Fields
    location   # ForeignKey(Location) - where counting
    created_by # ForeignKey(User) - who initiated
    status     # CharField(20) - in_progress/submitted/approved/rejected
    notes      # TextField - session notes
    created_at # DateTimeField - when started
    submitted_at # DateTimeField - when submitted
    approved_at  # DateTimeField - when approved
    
    # Relationships (reverse)
    items      # StockOpnameItem.session (reverse)
    
    # State Machine
    in_progress
        └─ submitted
            ├─ approved → creates Stock adjustments
            └─ rejected → revert to in_progress
    
    # Use: Physical inventory count workflow
```

#### StockOpnameItem
```python
class StockOpnameItem(models.Model):
    # Fields
    session       # ForeignKey(StockOpnameSession)
    variant       # ForeignKey(ProductVariant)
    current_stock # IntegerField - system quantity at count time
    counted_qty   # IntegerField - actual physical count
    notes         # TextField - item notes
    created_at    # DateTimeField
    
    # Unique Constraint
    UNIQUE: (session_id, variant_id) - only one count per item per session
    
    # Calculated Properties
    @property
    difference()      # counted_qty - current_stock (variance)
    @property
    is_accurate()     # difference == 0
    
    # Use: Physical count records
```

#### SupplierPrice
```python
class SupplierPrice(models.Model):
    # Fields
    vendor       # ForeignKey(Vendor)
    variant      # ForeignKey(ProductVariant)
    unit_price   # DecimalField(12,2) - price per unit
    currency     # CharField(3) - ISO code (IDR, USD, etc)
    minimum_quantity # IntegerField - MOQ
    maximum_quantity # IntegerField - max order qty (nullable)
    lead_time_days   # IntegerField - delivery time
    is_active    # BooleanField - active price
    is_preferred # BooleanField - preferred supplier
    last_updated_by  # ForeignKey(User) - who last updated
    effective_date   # DateField - when price starts
    valid_until      # DateField - when price ends
    created_at   # DateTimeField
    updated_at   # DateTimeField
    
    # Unique Constraint
    UNIQUE: (vendor_id, variant_id) - one price per vendor-product
    
    # Use: Purchase order pricing lookup
```

---

### 4. Workflow Models (4 models)
Stock requisition and transfer workflows.

#### Requisition
```python
class Requisition(models.Model):
    # Fields
    from_location # ForeignKey(Location)
    to_location   # ForeignKey(Location)
    requested_by  # ForeignKey(User)
    approved_by   # ForeignKey(User, nullable)
    status        # CharField(20) - waiting/approved/in_transit/completed/rejected
    created_at    # DateTimeField
    approved_at   # DateTimeField (nullable)
    
    # Relationships (reverse)
    items      # RequisitionItem.requisition (reverse)
    transfers  # Transfer.requisition (reverse, OneToOne in Transfer context)
    
    # State Machine
    waiting
        └─ approved
            └─ Transfer created automatically
                └─ in_transit
                    └─ completed
        └─ rejected
    
    # Use: Stock request between locations
```

#### RequisitionItem
```python
class RequisitionItem(models.Model):
    # Fields
    requisition # ForeignKey(Requisition)
    variant     # ForeignKey(ProductVariant)
    quantity    # PositiveIntegerField - requested qty
    
    # Unique Constraint
    UNIQUE: (requisition_id, variant_id) - one line per product
    
    # Use: Line items in requisition
```

#### Transfer
```python
class Transfer(models.Model):
    # Fields
    requisition           # ForeignKey(Requisition, nullable) - source requisition
    source_location       # ForeignKey(Location) - from where
    destination_location  # ForeignKey(Location) - where to
    created_by            # ForeignKey(User)
    status                # CharField(20) - pending/in_transit/received/cancelled
    notes                 # TextField
    created_at            # DateTimeField - when created
    sent_at               # DateTimeField (nullable) - when dispatched
    received_at           # DateTimeField (nullable) - when confirmed received
    
    # Relationships (reverse)
    items  # TransferItem.transfer (reverse)
    
    # State Machine
    pending
        └─ in_transit
            └─ received
        └─ cancelled
    
    # Use: Actual stock movement between locations
```

#### TransferItem
```python
class TransferItem(models.Model):
    # Fields
    transfer         # ForeignKey(Transfer)
    variant          # ForeignKey(ProductVariant)
    quantity_sent    # PositiveIntegerField - qty sent
    quantity_received # PositiveIntegerField (nullable) - qty confirmed received
    
    # Use: Line items in transfer
```

---

### 5. Order Models (2 models)
Sales orders and transactions.

#### Order
```python
class Order(models.Model):
    # Fields
    customer      # ForeignKey(Customer, nullable)
    customer_name # CharField(100) - for backward compatibility
    status        # CharField(20) - pending/completed/cancelled
    created_at    # DateTimeField - purchase timestamp
    
    # Relationships (reverse)
    items  # OrderItem.order (reverse)
    
    # Calculated Property
    @property
    total_price()  # Sum(items.quantity * items.price)
    
    # Use: Sales transaction (from POS)
```

#### OrderItem
```python
class OrderItem(models.Model):
    # Fields
    order    # ForeignKey(Order)
    variant  # ForeignKey(ProductVariant)
    quantity # PositiveIntegerField(default=1)
    price    # DecimalField(12,2) - price at time of sale (snapshot)
    
    # Use: Line items in order, price history
```

---

### 6. Recipe/Production Models (3 models)
Recipe management for manufactured products.

#### RecipeCategory
```python
class RecipeCategory(models.Model):
    # Fields
    name        # CharField(100) - UNIQUE
    description # TextField
    is_active   # BooleanField
    created_at  # DateTimeField
    updated_at  # DateTimeField
    
    # Relationships (reverse)
    recipes  # Recipe.category (reverse)
    
    # Use: Recipe classification (separate from product categories)
```

#### Recipe
```python
class Recipe(models.Model):
    # Fields
    name             # CharField(255) - UNIQUE
    description      # TextField
    instructions     # TextField - preparation steps
    category         # ForeignKey(RecipeCategory)
    yield_quantity   # DecimalField(12,2) - output amount
    yield_unit       # ForeignKey(Unit) - output unit
    preparation_time # IntegerField - minutes
    total_cost       # DecimalField(12,2) - calculated from ingredients
    cost_per_unit    # DecimalField(12,2) - total_cost / yield_quantity
    is_archived      # BooleanField
    created_at       # DateTimeField
    updated_at       # DateTimeField
    
    # Relationships (reverse)
    ingredients  # RecipeIngredient.recipe (reverse)
    
    # Calculated Method
    def recalculate_cost()  # Rebuild total_cost from ingredients
    
    # Calculated Property
    @property
    ingredient_count()  # Count of ingredients
    
    # Use: Product manufacturing recipe with cost tracking
```

#### RecipeIngredient
```python
class RecipeIngredient(models.Model):
    # Fields
    recipe        # ForeignKey(Recipe)
    variant       # ForeignKey(ProductVariant)
    quantity      # DecimalField(12,2) - amount needed
    unit          # ForeignKey(Unit)
    unit_cost     # DecimalField(12,2) - snapshot of variant.price_buy
    subtotal_cost # DecimalField(12,2) - quantity * unit_cost
    notes         # TextField
    created_at    # DateTimeField
    
    # Unique Constraint
    UNIQUE: (recipe_id, variant_id) - each ingredient once per recipe
    
    # Override save()
    - Snapshot unit_cost from variant.price_buy
    - Calculate subtotal_cost
    - Trigger recipe.recalculate_cost()
    
    # Override delete()
    - Trigger recipe.recalculate_cost()
    
    # Use: Ingredient tracking with cost history
```

---

### 7. User Models (2 models)
User management and profile extensions.

#### UserProfile
```python
class UserProfile(models.Model):
    # Fields
    user     # OneToOneField(User) - unique link
    location # ForeignKey(Location, nullable)
    
    # Use: Extend Django User with app-specific data
```

#### User
```python
# Django built-in User model (auth_user table)
Model from: from django.contrib.auth.models import User

# Linked to:
- UserProfile (OneToOne)
- Requisition.requested_by
- Requisition.approved_by
- Transfer.created_by
- StockOpnameSession.created_by
- SupplierPrice.last_updated_by
- SalesTarget.created_by
- RecipeIngredient (implicit via save history)
```

---

### 8. Target Models (1 model)
Sales targets and goals.

#### SalesTarget
```python
class SalesTarget(models.Model):
    # Fields
    year           # IntegerField - fiscal year
    month          # IntegerField - 1-12
    target_amount  # DecimalField(15,2) - revenue target in Rp
    notes          # TextField
    created_by     # ForeignKey(User, nullable)
    created_at     # DateTimeField
    updated_at     # DateTimeField
    
    # Unique Constraint
    UNIQUE: (year, month) - one target per month
    
    # Calculated Property
    @property
    target_daily()  # target_amount / 26 (working days)
    
    # Use: Sales goal tracking and reporting
```

---

## 📊 Relationship Diagrams

### Diagram 1: Product & Inventory (Core)
```
Product ──1:M──> ProductVariant ──1:M──> ProductAttribute
    │
    M
    │
    └─has─> Category
    └─has─> Unit
    └─has─> Vendor
    └─has─> Tax

ProductVariant
    │
    ├──1:M──> Stock ──M:1──> Location
    │
    ├──1:M──> SupplierPrice ──M:1──> Vendor
    │
    └──1:M──> RecipeIngredient ──M:1──> Recipe
```

### Diagram 2: Stock Management & Workflow
```
Location
    ├──1:M──> Stock ──M:1──> ProductVariant
    │
    ├──1:M──> StockOpnameSession ──1:M──> StockOpnameItem
    │                                          │
    │                                          M
    │                                          │
    │                                          └──ProductVariant
    │
    ├──1:M──> Requisition
    │              │
    │              ├──1:M──> RequisitionItem ──M:1──> ProductVariant
    │              │
    │              └──1:1──> Transfer (reverse)
    │
    └──1:M──> Transfer ──1:M──> TransferItem ──M:1──> ProductVariant
         │
         └──M:1──> Requisition (nullable)
```

### Diagram 3: Sales & Customers
```
Customer ──1:M──> Order ──1:M──> OrderItem ──M:1──> ProductVariant
    │
    └─has─> loyalty_points
    └─has─> tier (bronze/silver/gold/platinum)
    └─has─> total_spent
    └─has─> total_orders
```

### Diagram 4: Production & Recipes
```
RecipeCategory ──1:M──> Recipe
                            │
                            ├─has─> RecipeIngredient
                            │           │
                            │           M
                            │           │
                            │           └──ProductVariant
                            │
                            └──calculated─> total_cost
                                          └──cost_per_unit
```

### Diagram 5: Multi-Location Flow
```
User ──1:1──> UserProfile ──M:1──> Location
    │
    ├──Created by Requisition
    ├──Approved Requisition
    ├──Created Transfer
    └──Initiated StockOpname

Location ──multiple relationships as shown in Diagram 2──|
```

---

## 🔄 Data Flow Patterns

### Pattern 1: Stock Movement (Normal Flow)
```
[Inventory Staff]
    │
    ├─1. Check stock_overview.html
    │       └─ Query: Stock.objects.filter(location_id=X)
    │
    ├─2. Click "Add Stock Movement"
    │       └─ Form: add_stock_movement.html
    │
    └─3. Submit Form
            ├─ Create Stock record
            │   ├─ variant_id
            │   ├─ location_id
            │   ├─ quantity (+ or -)
            │   └─ transaction_type
            │
            └─ Query: Stock.objects.filter(variant_id=X, location_id=Y)
                      .update(quantity=F('quantity') + delta)
```

### Pattern 2: Stock Opname Workflow
```
[Staff] → StockOpnameSession (in_progress)
    │
    ├─ Physically count items
    └─ Enter counts in StockOpnameItem
            ├─ variant_id
            ├─ current_stock (from Stock table)
            ├─ counted_qty (physical count input)
            └─ difference = counted_qty - current_stock

[Manager] → Review StockOpnameSession (submit status → submitted)
    │
    ├─ Review discrepancies
    └─ Approve (status → approved)
            └─ FOR EACH StockOpnameItem with difference:
                ├─ Get Stock record (variant_id, location_id)
                └─ UPDATE quantity = counted_qty
```

### Pattern 3: Requisition & Transfer
```
[System] 
│
├─ Requisition created (status = waiting)
│       ├─ from_location_id
│       ├─ to_location_id
│       ├─ RequisitionItem (product, qty)
│       └─ requested_by (User)
│
├─ [Manager] Reviews & Approves
│       ├─ Requisition.status = approved
│       ├─ Requisition.approved_by = User
│       └─ Auto-create Transfer
│
└─ Transfer (status = pending)
        ├─ requisition_id = FK
        ├─ source_location_id = from_location
        ├─ destination_location_id = to_location
        ├─ TransferItem (product, qty_sent, qty_received=NULL)
        └─ Status flow: pending → in_transit → received
```

### Pattern 4: Recipe Cost Calculation
```
[Admin] Creates RecipeIngredient
    │
    └─ RecipeIngredient.save():
            ├─ unit_cost = variant.price_buy (snapshot)
            ├─ subtotal_cost = quantity * unit_cost
            └─ recipe.recalculate_cost()
                    ├─ total_cost = SUM(ingredient.subtotal_cost)
                    ├─ cost_per_unit = total_cost / recipe.yield_quantity
                    └─ Recipe.objects.filter(pk=recipe.id).update(...)
```

### Pattern 5: Order Creation (POS)
```
[Cashier] pos.html
    │
    ├─ Select customer (lookup: Customer.email)
    ├─ Add items (lookup: ProductVariant.sku)
    ├─ Apply discount (if any)
    └─ Process payment
            │
            └─ Create Order
                    ├─ customer_id (nullable)
                    ├─ customer_name (from Customer.name)
                    ├─ status = pending
                    └─ THEN FOR EACH item:
                            └─ Create OrderItem
                                ├─ variant_id
                                ├─ quantity
                                └─ price (snapshot at time of sale)
                    
                    ├─ Calculate Order.total_price (via aggregation)
                    ├─ Update Customer.total_spent += total_price
                    ├─ Update Customer.total_orders += 1
                    ├─ Update Customer.last_order_date = now()
                    └─ Update Customer.loyalty_points += earned
```

---

## 🔗 Model Dependencies

### Dependency Tree
```
LEVEL 0 (No dependencies - Master Data):
├─ Category
├─ Unit
├─ Vendor
├─ Tax
├─ Location
├─ RecipeCategory
└─ User (Django)

LEVEL 1 (Depends only on Level 0):
├─ Product (→ Category, Unit, Vendor, Tax)
├─ Customer
├─ SalesTarget (→ User)
└─ UserProfile (→ User, Location)

LEVEL 2 (Depends on Levels 0-1):
├─ ProductVariant (→ Product)
├─ SupplierPrice (→ Vendor, ProductVariant, User)
├─ Recipe (→ RecipeCategory, Unit)
├─ Requisition (→ Location, User)
└─ Order (→ Customer, User-implicit)

LEVEL 3 (Depends on Levels 0-2):
├─ ProductAttribute (→ ProductVariant)
├─ Stock (→ ProductVariant, Location)
├─ StockOpnameSession (→ Location, User)
├─ RecipeIngredient (→ Recipe, ProductVariant, Unit)
├─ RequisitionItem (→ Requisition, ProductVariant)
├─ Transfer (→ Requisition, Location, User)
└─ Order Item (→ Order, ProductVariant)

LEVEL 4 (Depends on Levels 0-3):
├─ StockOpnameItem (→ StockOpnameSession, ProductVariant)
├─ TransferItem (→ Transfer, ProductVariant)
└─ ProductDetail View (→ all product-related tables)
```

### Cascade Delete Impact
```
IF Delete: Category
    THEN: Product.category_id → NULL (SET_NULL)

IF Delete: ProductVariant X
    THEN: 
        - ProductAttribute (cascade)
        - Stock (cascade)
        - RecipeIngredient (PROTECT - error if exists)
        - OrderItem (PROTECT - error if exists)
        - SupplierPrice (cascade)
        - RequisitionItem (PROTECT - error if exists)
        - StockOpnameItem (PROTECT - error if exists)
        - TransferItem (PROTECT - error if exists)

IF Delete: Location X
    THEN:
        - Stock for location X (cascade)
        - Requisition.from/to (cascade)
        - Transfer.source/dest (cascade)
        - StockOpnameSession (PROTECT)
        - UserProfile.location (SET_NULL)

IF Delete: User X
    THEN:
        - Requisition.requested_by = X (cascade)
        - Requisition.approved_by = X → NULL (SET_NULL)
        - Transfer.created_by = X (cascade)
        - StockOpnameSession.created_by = X (PROTECT)
        - Other: various (PROTECT or SET_NULL)
```

---

## ✅ Validation Checklist

### Before Migrating to Production

#### ✓ Database Setup
- [ ] Database created (PostgreSQL/MySQL)
- [ ] Database user created with proper permissions
- [ ] Connection settings in settings.py verified
- [ ] Test connection works: `python manage.py dbshell`

#### ✓ Django Configuration
- [ ] All models imported in `__init__.py`
- [ ] App added to INSTALLED_APPS in settings.py
- [ ] `python manage.py check` passes without errors
- [ ] No circular imports in models

#### ✓ Foreign Key Integrity
- [ ] All FK references point to existing models
- [ ] ON_DELETE actions (CASCADE, PROTECT, SET_NULL) appropriate
- [ ] FK columns nullable properly set
- [ ] Self-referencing FKs (Category.parent) validated

#### ✓ Constraints
- [ ] UNIQUE constraints correctly defined
- [ ] Composite unique constraints (year, month) verified
- [ ] Default values set appropriately
- [ ] Custom Meta constraints working

#### ✓ Indexes
- [ ] Frequently queried fields have indexes
- [ ] Composite indexes on multi-column filters
- [ ] Index names don't conflict
- [ ] Query performance acceptable

#### ✓ Relationships
- [ ] related_name attributes avoid conflicts
- [ ] Reverse relationships queryable
- [ ] M2M handled properly (not applicable here, all are FK)
- [ ] OneToOne constraints verify

#### ✓ Data Validation
- [ ] CharField max_length appropriate for storage
- [ ] DecimalField(max_digits, decimal_places) sufficient
- [ ] DateTimeField auto_now vs auto_now_add correct
- [ ] Choice fields cover all valid options

#### ✓ Model Properties & Methods
- [ ] Calculated properties don't trigger queries in loops
- [ ] @property methods optimized (use annotate in views)
- [ ] Custom save() methods don't cause infinite loops
- [ ] __str__ methods implemented for admin display

#### ✓ Natural Keys
- [ ] Email fields UNIQUE with db_index=True
- [ ] SKU field UNIQUE and indexed
- [ ] Name fields UNIQUE where appropriate
- [ ] Slug fields correct for URL usage

#### ✓ Audit Fields
- [ ] created_at fields use auto_now_add=True
- [ ] updated_at fields use auto_now=True
- [ ] User FK stored for who created/approved
- [ ] Timestamp fields never manually set

---

## 🔄 Migration Strategy

### Migration Approach
```bash
# Step 1: Create initial migrations
python manage.py makemigrations lumra_config

# Step 2: Review migrations
python manage.py showmigrations lumra_config

# Step 3: Apply migrations (dev)
python manage.py migrate lumra_config

# Step 4: Verify tables created
python manage.py dbshell
  > SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'lumra%';
  > .tables

# Step 5: Test model queries
python manage.py shell
  >>> from lumra_config.models import Product, Category
  >>> Category.objects.create(name='Test')
  >>> Product.objects.create(name='Test Product', category_id=1)
  >>> Product.objects.select_related('category').all()
```

### Data Seeding
```python
# Create fixture or seed script
from lumra_config.models import Unit, Tax, Location

# Units of measurement
Unit.objects.get_or_create(name='Kilogram', symbol='kg')
Unit.objects.get_or_create(name='Liter', symbol='L')

# Tax rates (Indonesia)
Tax.objects.get_or_create(name='PPN', rate=10.00)
Tax.objects.get_or_create(name='No Tax', rate=0.00)

# Locations
Location.objects.get_or_create(name='Jakarta Central')
Location.objects.get_or_create(name='Warehouse A')
```

### Troubleshooting Migrations
```bash
# If migration conflicts
python manage.py makemigrations --merge

# If need to rollback
python manage.py migrate lumra_config 0001  # go to first migration
python manage.py migrate lumra_config       # then forward again

# If schema out of sync
python manage.py migrate --fake-initial

# Show migration history
python manage.py showmigrations lumra_config --plan
```

---

## 👨‍💼 Django Admin Configuration

### Admin Registration
```python
# lumra_config/admin.py

from django.contrib import admin
from .models import (
    Category, Unit, Vendor, Tax, Location, Customer,
    Product, ProductVariant, ProductAttribute, Stock,
    StockOpnameSession, StockOpnameItem,
    Requisition, RequisitionItem, Transfer, TransferItem,
    Order, OrderItem,
    Recipe, RecipeCategory, RecipeIngredient,
    SupplierPrice, UserProfile, SalesTarget
)

# Master Data - Simple readonly
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    search_fields = ['name', 'code']
    list_filter = ['is_active']

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'is_active']

# Product - Inline variant management
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    fields = ['sku', 'size_weight', 'price_buy', 'price_sell']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'vendor', 'unit']
    search_fields = ['name']
    list_filter = ['category', 'is_active']
    inlines = [ProductVariantInline]

# Stock Management
@admin.register(StockOpnameSession)
class StockOpnameSessionAdmin(admin.ModelAdmin):
    list_display = ['location', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'location']
    readonly_fields = ['created_at', 'submitted_at', 'approved_at']

# Workflow
@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ['from_location', 'to_location', 'status', 'requested_by']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'approved_at']

# Orders
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    date_hierarchy = 'created_at'
```

---

## 📈 Model Query Examples

### Common Queries

```python
# Product with category
Product.objects.select_related('category', 'vendor', 'unit')

# Stock by location
Stock.objects.filter(location_id=1).select_related('variant__product')

# Products with total stock
from django.db.models import Sum
ProductVariant.objects.annotate(
    total_stock=Sum('stock_entries__quantity')
).filter(total_stock__lt=10)

# Orders this month
from django.utils import timezone
from datetime import timedelta
Order.objects.filter(
    created_at__gte=timezone.now() - timedelta(days=30)
).select_related('customer')

# Recipe cost details
Recipe.objects.prefetch_related(
    'ingredients__variant__product'
).get(id=1)
```

---

This comprehensive model documentation ensures database integrity and supports proper implementation.
