# ✅ LUMRA ERP - Database Verification & Implementation Guide
**Step-by-Step Checklist to Verify and Implement Database**  
*Generated: April 10, 2026*

---

## 📋 Table of Contents
1. [Pre-Migration Checklist](#pre-migration-checklist)
2. [Database Setup Steps](#database-setup-steps)
3. [Migration & Verification](#migration--verification)
4. [Data Integrity Tests](#data-integrity-tests)
5. [Performance Validation](#performance-validation)
6. [Django Admin Setup](#django-admin-setup)
7. [Troubleshooting Guide](#troubleshooting-guide)

---

## ✅ Pre-Migration Checklist

### Infrastructure Check
```
□ Database Server Running
  - PostgreSQL: psql --version
  - MySQL: mysql --version
  - SQLite: default with Django (test only)

□ Django Environment
  - virtualenv activated
  - requirements.txt installed: pip list
  - Django version 3.2+ : python -m django --version
  - Python 3.8+ : python --version

□ Database Credentials
  - Host: __________
  - Port: __________
  - Username: __________
  - Password: __________
  - Database name: lumra_erp (or your choice)

□ File Permissions
  - Django app directory writable
  - Database directory writable (Linux/Mac)
  - No antivirus blocking database files
```

### Code Quality Check
```
□ Models Review
  - All models defined in lumra_config/models.py
  - No circular imports between models
  - All imports at top of file work: python -c "from lumra_config import models"
  
□ Settings Configuration
  - DATABASES section configured correctly in settings.py
  - lumra_config added to INSTALLED_APPS
  - Database backend specified (postgresql/mysql/sqlite3)
  
□ Project Health
  - No Python syntax errors: python manage.py check
  - All apps can be loaded: python manage.py help
  - Settings validated: python manage.py validate_settings (if available)
```

### Backup & Planning
```
□ Current Database (if upgrading)
  - Backup existing database: BACKUP_FILENAME_YYYY_MM_DD.sql
  - Document current schema for reference
  - List of custom queries/views to preserve
  
□ Implementation Plan
  - Rollback plan if migration fails
  - Downtime window identified
  - Notification sent to users
  - Support team briefed on changes
```

---

## 🔧 Database Setup Steps

### Step 1: Create Database & User

#### PostgreSQL
```bash
# Connect as admin
sudo -u postgres psql

# Create database
CREATE DATABASE lumra_erp ENCODING 'UTF8';

# Create user
CREATE USER lumra_user WITH PASSWORD 'secure_password_here';

# Grant privileges
ALTER ROLE lumra_user SET client_encoding TO 'utf8';
ALTER ROLE lumra_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE lumra_user SET default_transaction_deferrable TO on;
ALTER ROLE lumra_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE lumra_erp TO lumra_user;

# Verify
\l          # list databases
\du         # list users
\q          # exit
```

#### MySQL
```bash
# Login
mysql -u root -p

# Create database
CREATE DATABASE lumra_erp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user
CREATE USER 'lumra_user'@'localhost' IDENTIFIED BY 'secure_password_here';

# Grant privileges
GRANT ALL PRIVILEGES ON lumra_erp.* TO 'lumra_user'@'localhost';
FLUSH PRIVILEGES;

# Verify
SHOW DATABASES;
SELECT user FROM mysql.user;
EXIT;
```

#### SQLite (Development Only)
```bash
# SQLite creates database automatically on first migration
# Just ensure file path is writable:
touch /path/to/db.sqlite3
chmod 644 /path/to/db.sqlite3
```

---

### Step 2: Configure Django Settings

#### settings.py - Database Connection
```python
# For PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lumra_erp',
        'USER': 'lumra_user',
        'PASSWORD': 'secure_password_here',
        'HOST': 'localhost',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}

# For MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lumra_erp',
        'USER': 'lumra_user',
        'PASSWORD': 'secure_password_here',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# For SQLite (Development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Logging for debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

#### settings.py - App Registration
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'lumra_config',  # ← Add your app here
]
```

---

### Step 3: Test Database Connection

```bash
# Test connection from Django
python manage.py dbshell

# Should open database shell (psql, mysql>, or sqlite>)
# Type: .exit or \q to quit

# Test from Python
python manage.py shell
>>> from django.db import connection
>>> with connection.cursor() as cursor:
...     cursor.execute("SELECT 1")
...     print(cursor.fetchone())
# Should print: (1,) or [1]
```

---

## 🔄 Migration & Verification

### Step 4: Create Migrations

```bash
# Check for issues first
python manage.py check

# Create migration files from models
python manage.py makemigrations lumra_config

# Review generated migrations
# Look in: lumra_config/migrations/0001_initial.py
# Should show all 32+ models

# Show migration plan
python manage.py showmigrations lumra_config
```

**Expected Output:**
```
lumra_config
 [ ] 0001_initial

1 migration for 'lumra_config'
```

---

### Step 5: Apply Migrations

```bash
# Dry run (show what would happen)
python manage.py migrate lumra_config --plan

# Apply migrations
python manage.py migrate lumra_config

# Expected output should show all tables being created
```

**Expected Output:**
```
Running migrations:
  Applying lumra_config.0001_initial... OK
```

---

### Step 6: Verify Schema Created

```bash
# Check via Django shell
python manage.py shell
>>> from django.db import connection
>>> tables = connection.introspection.table_names()
>>> lumra_tables = [t for t in tables if 'lumra' in t or t.startswith('_') or t.startswith('production')]
>>> for table in sorted(lumra_tables):
...     print(table)

# Should list all your tables:
# _categories
# _units
# _vendors
# _taxes
# lumra_config_customers
# lumra_config_locations
# lumra_config_orderitems
# lumra_config_orders
# lumra_config_products
# lumra_config_productattribute_items
# lumra_config_productvariants
# lumra_config_requisitionitem
# lumra_config_requisitions
# lumra_config_stock
# lumra_config_stockopname_item
# lumra_config_stockopname_session
# lumra_config_sales_targets
# lumra_config_supplier_prices
# lumra_config_transfers
# lumra_config_transferitem
# lumra_config_userprofile
# production_recipe_categories
# production_recipes
# production_recipe_ingredients
```

---

### Step 7: Inspect Table Structure

#### PostgreSQL
```sql
-- Connect to database
\d _categories;          -- Show category table structure
\d lumra_config_products;
\d lumra_config_stock;
\di                      -- List all indexes
\d+ lumra_config_productvariants;  -- Show with details
```

#### MySQL
```sql
-- Show table structure
DESCRIBE _categories;
DESCRIBE lumra_config_products;
SHOW INDEX FROM lumra_config_stock;
SHOW TABLES LIKE 'lumra%';
```

#### SQLite
```sql
-- Show schema
.schema _categories
.schema lumra_config_products
.tables
.index lumra_config_stock
```

---

## 🧪 Data Integrity Tests

### Test 1: Foreign Key Constraints

```python
# lumra_config/tests.py or run via shell
from lumra_config.models import Product, Category, Vendor, Unit, Tax

# Create test data
category = Category.objects.create(name='Test Category', code='TST')
vendor = Vendor.objects.create(name='Test Vendor', code='TV')
unit = Unit.objects.create(name='Kilogram', symbol='kg')
tax = Tax.objects.create(name='Test Tax', rate=10.00)

# Create product with FK
product = Product.objects.create(
    name='Test Product',
    category=category,
    vendor=vendor,
    unit=unit,
    tax=tax
)

# Verify relationships
print(product.category.name)  # Should print: Test Category
print(product.vendor.name)    # Should print: Test Vendor
print(product.unit.name)      # Should print: Kilogram
print(product.tax.name)       # Should print: Test Tax

# ✓ PASS if no errors
```

### Test 2: Cascade Delete

```python
# Test that deletes cascade properly
from lumra_config.models import Product, ProductVariant

product = Product.objects.create(name='Delete Test')
variant = ProductVariant.objects.create(
    product=product,
    sku='DELTEST001',
    price_buy=10000,
    price_sell=15000
)

# Before delete
print(ProductVariant.objects.count())  # Should show 1

# Delete product
product.delete()

# After delete
print(ProductVariant.objects.count())  # Should show 0

# ✓ PASS if variant cascade deleted
```

### Test 3: Unique Constraints

```python
from lumra_config.models import Category, Unit, Location

# Try to create duplicate
category1 = Category.objects.create(name='Unique Test', code='UT')

try:
    category2 = Category.objects.create(name='Unique Test', code='UT2')
    print("✗ FAIL - duplicate not prevented")
except Exception as e:
    print("✓ PASS - duplicate prevented:", str(e))

# Clean up
category1.delete()
```

### Test 4: Hierarchical Data (Category Parent)

```python
from lumra_config.models import Category

# Create hierarchy
root = Category.objects.create(name='Beverages', code='BEV')
hot = Category.objects.create(name='Hot Drinks', code='HOT', parent=root)
coffee = Category.objects.create(name='Coffee', code='COF', parent=hot)
tea = Category.objects.create(name='Tea', code='TEA', parent=hot)

# Test hierarchy
print(coffee.parent.name)        # Should print: Hot Drinks
print(hot.parent.name)           # Should print: Beverages
print(root.parent)               # Should print: None

# Reverse relationships
print(hot.category_set.count())  # Should print: 2 (coffee, tea)

# ✓ PASS if hierarchy works
```

### Test 5: DecimalField Precision

```python
from lumra_config.models import ProductVariant, SupplierPrice
from decimal import Decimal

# Test decimal precision (10 digits, 2 decimal places)
variant = ProductVariant.objects.create(
    sku='DECIMAL_TEST',
    price_buy=Decimal('123456789.99'),  # Max valid
    price_sell=Decimal('123456789.99')
)

print(variant.price_buy)  # Should print: 123456789.99

# Try to exceed (should fail or truncate)
try:
    variant.price_buy = Decimal('1234567890.00')  # Too big
    variant.save()
    print("Value truncated or rejected")
except Exception as e:
    print("✓ PASS - value validation:", str(e))

# ✓ PASS if decimal handling correct
```

---

## 🚀 Performance Validation

### Performance Test 1: Index Usage

```python
# Check if indexes are being used
from django.db import connection
from django.test.utils import CaptureQueriesContext
from lumra_config.models import ProductVariant, Stock

# Create test data
for i in range(1000):
    variant = ProductVariant.objects.create(
        sku=f'PERF_TEST_{i}',
        price_buy=1000,
        price_sell=1500
    )

# Test indexed query
with CaptureQueriesContext(connection) as context:
    result = ProductVariant.objects.filter(sku='PERF_TEST_500').first()

print(f"Query count: {len(context.captured_queries)}")  # Should be 1
print(f"Query time: {context.captured_queries[0]['time']}")

# ✓ PASS if takes < 0.1 seconds with index
```

### Performance Test 2: N+1 Query Detection

```python
from django.db import connection
from django.test.utils import CaptureQueriesContext
from lumra_config.models import Product

# Create test data
for i in range(100):
    Product.objects.create(name=f'Product {i}', category_id=None)

# ✗ BAD: N+1 queries
with CaptureQueriesContext(connection) as context:
    products = Product.objects.all()
    for product in products:
        _ = product.category  # Trigger query per product

bad_queries = len(context.captured_queries)
print(f"BAD approach: {bad_queries} queries")  # Will be ~101

# ✓ GOOD: Using select_related
with CaptureQueriesContext(connection) as context:
    products = Product.objects.select_related('category').all()
    for product in products:
        _ = product.category  # Already loaded

good_queries = len(context.captured_queries)
print(f"GOOD approach: {good_queries} queries")  # Will be 2

print(f"Improvement: {bad_queries - good_queries}x fewer queries")
# ✓ PASS if GOOD is significantly lower
```

### Performance Test 3: Bulk Operations

```python
import time
from lumra_config.models import Stock, ProductVariant, Location

variant = ProductVariant.objects.first()
location = Location.objects.create(name='Perf Test Location')

# ✗ SLOW: Individual creates
start = time.time()
for i in range(1000):
    Stock.objects.create(
        variant=variant,
        location=location,
        quantity=i,
        transaction_type='in'
    )
slow_time = time.time() - start

# ✓ FAST: Bulk create
Stock.objects.all().delete()
start = time.time()
stocks = [Stock(
    variant=variant,
    location=location,
    quantity=i,
    transaction_type='in'
) for i in range(1000)]
Stock.objects.bulk_create(stocks, batch_size=100)
fast_time = time.time() - start

print(f"Individual: {slow_time:.2f}s")
print(f"Bulk: {fast_time:.2f}s")
print(f"Improvement: {slow_time/fast_time:.1f}x faster")

# ✓ PASS if bulk is 10x+ faster
```

---

## 👨‍💼 Django Admin Setup

### Step 8: Configure Admin Interface

```python
# lumra_config/admin.py

from django.contrib import admin
from .models import *

# Register all models
admin.site.register(Category)
admin.site.register(Unit)
admin.site.register(Vendor)
admin.site.register(Tax)
admin.site.register(Location)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductAttribute)
admin.site.register(Stock)
admin.site.register(StockOpnameSession)
admin.site.register(StockOpnameItem)
admin.site.register(Requisition)
admin.site.register(RequisitionItem)
admin.site.register(Transfer)
admin.site.register(TransferItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Recipe)
admin.site.register(RecipeCategory)
admin.site.register(RecipeIngredient)
admin.site.register(SupplierPrice)
admin.site.register(UserProfile)
admin.site.register(SalesTarget)
```

### Step 9: Create Superuser

```bash
# Create first admin user
python manage.py createsuperuser

# Prompted for:
# Username: admin
# Email: admin@example.com
# Password: (hidden)
# Password (again): (hidden)

# Should show: Superuser created successfully.
```

### Step 10: Test Admin Interface

```bash
# Start Django development server
python manage.py runserver

# Access admin: http://localhost:8000/admin/
# Login with superuser credentials

# You should see:
# - Groups
# - Users
# - [lumra_config] - All your models listed
```

---

## 🐛 Troubleshooting Guide

### Problem 1: "No module named 'lumra_config'"

```
Error: ModuleNotFoundError: No module named 'lumra_config'

Solution:
1. Verify app folder exists: ls lumra_config/
2. Check __init__.py exists: ls lumra_config/__init__.py
3. Add to INSTALLED_APPS in settings.py
4. Restart Django process
```

### Problem 2: "Table does not exist"

```
Error: django.db.utils.ProgrammingError: relation "lumra_config_..." does not exist

Solution:
1. Run migrations: python manage.py migrate lumra_config
2. Verify migrations applied: python manage.py showmigrations lumra_config
3. Check database: python manage.py dbshell → \dt (PostgreSQL)
4. If using fresh DB, may need: python manage.py migrate --fake-initial
```

### Problem 3: "Duplicate entry for key"

```
Error: IntegrityError: UNIQUE constraint failed

Solution:
1. Identify which field (check error message)
2. Check for duplicate data: SELECT field, COUNT(*) FROM table GROUP BY field HAVING COUNT(*) > 1
3. Delete duplicates or clean data
4. Retry operation
```

### Problem 4: "Foreign key constraint failed"

```
Error: IntegrityError: 1452 - Cannot add or update a child row

Solution:
1. Check FK value exists in parent table
2. Example: Verify category_id exists in _categories table
3. Use: SELECT * FROM _categories WHERE id = X
4. Fix: Create parent before child, or set FK to NULL if nullable
```

### Problem 5: Migration File Conflicts

```
Error: There are conflicting migrations

Solution:
1. Review conflicting migrations
2. Choose one or merge: python manage.py makemigrations --merge
3. Resolve conflicts in generated merge file
4. Re-run: python manage.py migrate lumra_config
```

### Problem 6: Decimal Field Errors

```
Error: ValueError: [Decimal(...)]: unsupported operand type(s)

Solution:
1. Import Decimal: from decimal import Decimal
2. Use Decimal for pricing: Decimal('123.45') not 123.45
3. Never mix Decimal with float
4. Store prices as Decimal in database, convert only for display
```

---

## 📊 Database Health Checks

### Regular Maintenance

```bash
# PostgreSQL - Analyze and vacuum
python manage.py dbshell
>>> VACUUM ANALYZE;
>>> \q

# MySQL - Optimize tables
python manage.py dbshell
>>> OPTIMIZE TABLE _categories, _units, lumra_config_products;
>>> EXIT;

# SQLite - Vacuum (in Django shell)
python manage.py shell
>>> from django.db import connection
>>> connection.cursor().execute('VACUUM')
```

### Backup Strategy

```bash
# PostgreSQL
pg_dump -U lumra_user lumra_erp > backup_2026_04_10.sql
pg_dump -U lumra_user lumra_erp | gzip > backup_2026_04_10.sql.gz

# MySQL
mysqldump -u lumra_user -p lumra_erp > backup_2026_04_10.sql
mysqldump -u lumra_user -p lumra_erp | gzip > backup_2026_04_10.sql.gz

# SQLite
cp db.sqlite3 backup_2026_04_10.sqlite3
```

### Restore from Backup

```bash
# PostgreSQL
psql -U lumra_user lumra_erp < backup_2026_04_10.sql

# MySQL
mysql -u lumra_user -p lumra_erp < backup_2026_04_10.sql

# SQLite
cp backup_2026_04_10.sqlite3 db.sqlite3
```

---

## ✅ Final Verification Checklist

Before going to production:

```
FUNCTIONALITY
□ All models successfully migrated
□ Admin interface accessible
□ Can create/read/update/delete records
□ Foreign key relationships work
□ Unique constraints enforced
□ Cascade deletes working
□ Calculated properties function

PERFORMANCE
□ Indexes created on critical fields
□ Query performance < 100ms for common operations
□ No N+1 query problems detected
□ Bulk operations optimized
□ Database size acceptable

SECURITY
□ Database credentials secured (not in version control)
□ User permissions properly set
□ Database connection encrypted (if remote)
□ Backup strategy in place
□ Regular maintenance scheduled

DATA INTEGRITY
□ No orphaned records
□ Referential integrity maintained
□ Decimal/currency fields precise
□ Timestamps accurate
□ Soft deletes working if implemented

DOCUMENTATION
□ Schema documented
□ Data dictionary created
□ Migration history preserved
□ Backup schedule documented
□ Disaster recovery plan tested
```

---

**Once all checks pass, your database is ready for production use!**
