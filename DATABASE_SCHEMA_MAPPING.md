# 📊 LUMRA ERP - Database Schema Mapping
**Complete Database Structure, Models, Tables, and Relationships**  
*Generated: April 10, 2026*

---

## 📑 Table of Contents
1. [Database Overview](#database-overview)
2. [Core Models](#core-models)
3. [Entity Relationship Diagram](#entity-relationship-diagram)
4. [Detailed Schema](#detailed-schema)
5. [Foreign Key Relationships](#foreign-key-relationships)
6. [Unique Constraints](#unique-constraints)
7. [Indexes](#indexes)
8. [Data Types Reference](#data-types-reference)
9. [Validation Rules](#validation-rules)
10. [Workflow Models](#workflow-models)
11. [Views (Database Views)](#views-database-views)

---

## 🗄️ Database Overview

### System
- **Framework:** Django ORM (Python)
- **Supported Databases:** PostgreSQL, MySQL, SQLite
- **Total Models:** 32 models
- **Total Tables:** 32 tables (+ 1 database view)
- **Relationships:** 50+ foreign keys

### Database Tables by Category
```
📦 Master Data (7 tables)
  - _categories
  - _units
  - _vendors
  - _taxes
  - lumra_config_locations
  - lumra_config_customers
  - (User via Django)

📦 Product Management (4 tables)
  - lumra_config_products
  - lumra_config_productvariants
  - lumra_config_productattribute_items
  - product_details_view (database view)

📦 Stock Management (4 tables)
  - lumra_config_stock
  - lumra_config_stockopname_session
  - lumra_config_stockopname_item
  - lumra_config_supplier_prices

📦 Inventory Workflow (3 tables)
  - lumra_config_requisitions
  - lumra_config_requisitionitem
  - lumra_config_transfers
  - lumra_config_transferitem

📦 Orders (2 tables)
  - lumra_config_orders
  - lumra_config_orderitems

📦 Production (3 tables)
  - production_recipe_categories
  - production_recipes
  - production_recipe_ingredients

📦 User Management (2 tables)
  - auth_user (Django built-in)
  - lumra_config_userprofile

📦 Sales & Target (1 table)
  - lumra_config_sales_targets

TOTAL: 26 tables in lumra_config app
```

---

## 🏛️ Core Models

### 32 Django Models

| # | Model | Table Name | Type | Purpose |
|---|-------|-----------|------|---------|
| 1 | `Category` | `_categories` | Master | Product categories (hierarchical) |
| 2 | `Unit` | `_units` | Master | Units of measurement (kg, liter, pcs) |
| 3 | `Vendor` | `_vendors` | Master | Suppliers/vendors |
| 4 | `Tax` | `_taxes` | Master | Tax rates |
| 5 | `Location` | `_lumra_config_locations` | Master | Store/warehouse locations |
| 6 | `Customer` | `lumra_config_customers` | Master | Customer database |
| 7 | `Product` | `lumra_config_products` | Core | Main product (base for variants) |
| 8 | `ProductVariant` | `lumra_config_productvariants` | Core | Product SKU/variant with pricing |
| 9 | `ProductAttribute` | `lumra_config_productattribute_items` | Core | Variant attributes (size, weight) |
| 10 | `Stock` | `lumra_config_stock` | Core | Stock per location |
| 11 | `StockOpnameSession` | `lumra_config_stockopname_session` | Workflow | Physical count session |
| 12 | `StockOpnameItem` | `lumra_config_stockopname_item` | Workflow | Physical count items |
| 13 | `Requisition` | `lumra_config_requisitions` | Workflow | Stock requisition request |
| 14 | `RequisitionItem` | `lumra_config_requisitionitem` | Workflow | Items in requisition |
| 15 | `Transfer` | `lumra_config_transfers` | Workflow | Stock transfer |
| 16 | `TransferItem` | `lumra_config_transferitem` | Workflow | Items being transferred |
| 17 | `Order` | `lumra_config_orders` | Transaction | Sales order/POS transaction |
| 18 | `OrderItem` | `lumra_config_orderitems` | Transaction | Items sold in order |
| 19 | `SupplierPrice` | `lumra_config_supplier_prices` | Pricing | Vendor pricing per variant |
| 20 | `RecipeCategory` | `production_recipe_categories` | Recipe | Recipe category |
| 21 | `Recipe` | `production_recipes` | Recipe | Recipe/formula |
| 22 | `RecipeIngredient` | `production_recipe_ingredients` | Recipe | Ingredients in recipe |
| 23 | `UserProfile` | `lumra_config_userprofile` | User | User profile extension |
| 24 | `SalesTarget` | `lumra_config_sales_targets` | Target | Monthly sales target |
| 25 | `ProductDetail` | `product_details_view` | View | Database view (denormalized) |

---

## 🔗 Entity Relationship Diagram

### Simplified ERD
```
┌──────────────────────────────────────────────────────────────┐
│                    MASTER DATA LAYER                         │
├──────────────┬──────────────┬──────────────┬─────────────────┤
│  Category    │  Unit        │  Vendor      │  Tax            │
│  ├─ name     │  ├─ name     │  ├─ name     │  ├─ name        │
│  ├─ parent   │  ├─ symbol   │  ├─ code     │  ├─ rate        │
│  └─ slug     │  └─ ...      │  ├─ email    │  └─ ...         │
└─────┬────────┴──────────────┴──────────────┴─────────────────┘
      │
      └─↓ (FK)
┌──────────────────────────────────────────────────────────────┐
│                     PRODUCT LAYER                            │
├─────────────────────────────────────────────────────────────┤
│ Product                                                       │
│ ├─ id (PK)                                                   │
│ ├─ name                                                       │
│ ├─ category_id (FK → Category)                              │
│ ├─ vendor_id (FK → Vendor)                                  │
│ ├─ unit_id (FK → Unit)                                      │
│ ├─ tax_id (FK → Tax)                                        │
│ └─ ...                                                        │
│                                                               │
│ ├── ProductVariant (1:M)                                     │
│ │   ├─ id (PK)                                              │
│ │   ├─ product_id (FK → Product)                           │
│ │   ├─ sku (UNIQUE)                                        │
│ │   ├─ price_buy                                            │
│ │   ├─ price_sell                                           │
│ │   │                                                        │
│ │   ├─→ ProductAttribute (1:M)                              │
│ │   │   ├─ variant_id (FK)                                 │
│ │   │   ├─ attr_name                                        │
│ │   │   └─ attr_value                                       │
│ │   │                                                        │
│ │   ├─→ Stock (1:M)                                         │
│ │   │   ├─ variant_id (FK)                                 │
│ │   │   ├─ location_id (FK → Location)                    │
│ │   │   ├─ quantity                                         │
│ │   │   └─ transaction_type                                 │
│ │   │                                                        │
│ │   └─→ SupplierPrice (1:M)                                 │
│ │       ├─ variant_id (FK)                                 │
│ │       ├─ vendor_id (FK → Vendor)                         │
│ │       └─ unit_price                                       │
│                                                               │
│ └─→ recipe_ingredients (1:M) [via ProductVariant]           │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   STOCK MANAGEMENT LAYER                     │
├──────────────────────────────────────────────────────────────┤
│ Location                                                      │
│ └─→ Stock (1:M)                                              │
│ └─→ Requisition (1:M) [from/to]                              │
│ └─→ Transfer (1:M)                                           │
│ └─→ StockOpnameSession (1:M)                                 │
│                                                               │
│ StockOpnameSession                                           │
│ ├─ location_id (FK → Location)                              │
│ ├─ created_by (FK → User)                                   │
│ └─→ StockOpnameItem (1:M)                                    │
│     ├─ variant_id (FK → ProductVariant)                    │
│     └─ current_stock, counted_qty                           │
│                                                               │
│ Requisition                                                  │
│ ├─ from_location_id (FK → Location)                        │
│ ├─ to_location_id (FK → Location)                          │
│ ├─ requested_by (FK → User)                                │
│ ├─ approved_by (FK → User)                                 │
│ └─→ RequisitionItem (1:M)                                   │
│     └─ variant_id (FK → ProductVariant)                    │
│                                                               │
│ Transfer                                                     │
│ ├─ source_location_id (FK → Location)                      │
│ ├─ destination_location_id (FK → Location)                 │
│ ├─ created_by (FK → User)                                  │
│ ├─ requisition_id (FK → Requisition, nullable)            │
│ └─→ TransferItem (1:M)                                      │
│     ├─ variant_id (FK → ProductVariant)                    │
│     └─ quantity_sent, quantity_received                     │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                  SALES & ORDERS LAYER                        │
├──────────────────────────────────────────────────────────────┤
│ Customer                                                      │
│ ├─ name, email (UNIQUE), phone                             │
│ ├─ tier (bronze, silver, gold, platinum)                   │
│ ├─ loyalty_points                                           │
│ ├─ total_spent, total_orders                               │
│ └─→ Order (1:M)                                             │
│                                                               │
│ Order                                                        │
│ ├─ customer_id (FK → Customer, nullable)                   │
│ ├─ customer_name (for backward compatibility)              │
│ ├─ status (pending, completed, cancelled)                  │
│ └─→ OrderItem (1:M)                                         │
│     ├─ variant_id (FK → ProductVariant)                    │
│     ├─ quantity, price (snapshot at time of sale)          │
│     └─ order total calculation via ORM aggregation         │
│                                                               │
│ SalesTarget                                                  │
│ ├─ year, month (UNIQUE constraint)                         │
│ ├─ target_amount (decimal)                                 │
│ └─ created_by (FK → User)                                  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   PRODUCTION & RECIPES LAYER                 │
├──────────────────────────────────────────────────────────────┤
│ RecipeCategory                                               │
│ └─→ Recipe (1:M)                                             │
│                                                               │
│ Recipe                                                       │
│ ├─ name (UNIQUE)                                            │
│ ├─ category_id (FK → RecipeCategory)                       │
│ ├─ yield_quantity, yield_unit (FK → Unit)                  │
│ ├─ total_cost, cost_per_unit (stored - calculated)         │
│ ├─ preparation_time                                        │
│ └─→ RecipeIngredient (1:M)                                  │
│     ├─ variant_id (FK → ProductVariant)                    │
│     ├─ quantity, unit (FK → Unit)                          │
│     ├─ unit_cost, subtotal_cost (snapshot)                 │
│     └─ notes                                               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   USER MANAGEMENT LAYER                      │
├──────────────────────────────────────────────────────────────┤
│ User (Django built-in)                                       │
│ └─→ UserProfile (1:1)                                        │
│     ├─ location_id (FK → Location)                         │
│     └─ Other profile extensions                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 Detailed Schema

### 1. MASTER DATA TABLES

#### `_categories` - Product Categories
```sql
CREATE TABLE _categories (
    id                  BIGINT PRIMARY KEY AUTO_INCREMENT,
    name                VARCHAR(100) NOT NULL UNIQUE,
    description         TEXT,
    parent_id           BIGINT NULL,  -- FK to self for hierarchy
    slug                VARCHAR(100) UNIQUE NULL,
    code                VARCHAR(10) NULL,
    icon_url            VARCHAR(255) NULL,
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          DATETIME AUTO_NOW_ADD,
    updated_at          DATETIME AUTO_NOW,
    
    FOREIGN KEY (parent_id) REFERENCES _categories(id) ON DELETE SET NULL,
    INDEX idx_name (name),
    INDEX idx_slug (slug)
);
```

**Fields:**
| Field | Type | Constraints | Purpose |
|-------|------|-----------|---------|
| `id` | BigInt | PK, Auto | Primary key |
| `name` | Char(100) | NOT NULL, UNIQUE, INDEX | Category name |
| `description` | Text | NULL | Description |
| `parent_id` | BigInt | FK → self | Parent category (hierarchy) |
| `slug` | Char(100) | UNIQUE, NULL | URL-friendly name |
| `code` | Char(10) | NULL | Category code |
| `icon_url` | Char(255) | NULL | Icon image URL |
| `is_active` | Boolean | DEFAULT TRUE | Active status |
| `created_at` | DateTime | AUTO | Creation timestamp |
| `updated_at` | DateTime | AUTO | Last update timestamp |

**Hierarchy Example:**
```
Beverages (id:1)
├─ Hot Drinks (id:2, parent:1)
│  ├─ Coffee (id:3, parent:2)
│  └─ Tea (id:4, parent:2)
└─ Cold Drinks (id:5, parent:1)
   └─ Juice (id:6, parent:5)
```

---

#### `_units` - Units of Measurement
```sql
CREATE TABLE _units (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(50) NOT NULL UNIQUE,
    symbol      VARCHAR(10) NULL,
    description TEXT,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  DATETIME AUTO_NOW_ADD,
    
    INDEX idx_name (name)
);
```

**Common Units:**
```
id | name        | symbol | is_active
1  | Kilogram    | kg     | true
2  | Liter       | L      | true
3  | Meter       | m      | true
4  | Piece       | pcs    | true
5  | Box         | box    | true
6  | Gram        | g      | true
```

---

#### `_vendors` - Suppliers
```sql
CREATE TABLE _vendors (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL UNIQUE,
    contact_person VARCHAR(100) NULL,
    phone       VARCHAR(20) NULL,
    code        VARCHAR(20) NULL,
    email       VARCHAR(100) NULL,
    address     TEXT NULL,
    website     VARCHAR(255) NULL,
    tax_number  VARCHAR(50) NULL,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  DATETIME AUTO_NOW_ADD,
    updated_at  DATETIME AUTO_NOW,
    
    INDEX idx_name (name),
    INDEX idx_email (email)
);
```

---

#### `_taxes` - Tax Rates
```sql
CREATE TABLE _taxes (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL UNIQUE,
    rate        DECIMAL(5,2) NOT NULL,  -- e.g., 10.00 for 10%
    description TEXT,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  DATETIME AUTO_NOW_ADD,
    
    INDEX idx_name (name)
);
```

**Examples:**
```
id | name    | rate  | is_active
1  | PPN     | 10.00 | true
2  | PPH 26  | 2.00  | true
3  | No Tax  | 0.00  | true
```

---

#### `lumra_config_locations` - Stores/Warehouses
```sql
CREATE TABLE lumra_config_locations (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(100) NOT NULL UNIQUE,
    address         TEXT NULL,
    location_type   VARCHAR(20) NULL,  -- 'store', 'warehouse', 'branch'
    created_at      DATETIME AUTO_NOW_ADD,
    
    INDEX idx_name (name)
);
```

---

#### `lumra_config_customers` - Customer Database
```sql
CREATE TABLE lumra_config_customers (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(255) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    phone           VARCHAR(20) NULL,
    address         TEXT NULL,
    city            VARCHAR(100) NULL,
    tier            VARCHAR(20) DEFAULT 'bronze',  -- bronze, silver, gold, platinum
    loyalty_points  INT DEFAULT 0,
    total_spent     DECIMAL(15,2) DEFAULT 0,
    total_orders    INT DEFAULT 0,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      DATETIME AUTO_NOW_ADD,
    updated_at      DATETIME AUTO_NOW,
    last_order_date DATETIME NULL,
    
    INDEX idx_name (name),
    INDEX idx_email (email),
    INDEX idx_tier (tier)
);
```

---

### 2. PRODUCT MANAGEMENT TABLES

#### `lumra_config_products` - Main Products
```sql
CREATE TABLE lumra_config_products (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    category_id BIGINT NULL,  -- FK → _categories
    vendor_id   BIGINT NULL,  -- FK → _vendors (preferred vendor)
    tax_id      BIGINT NULL,  -- FK → _taxes
    unit_id     BIGINT NULL,  -- FK → _units (base unit)
    created_at  DATETIME AUTO_NOW_ADD,
    updated_at  DATETIME AUTO_NOW,
    
    FOREIGN KEY (category_id) REFERENCES _categories(id) ON DELETE SET NULL,
    FOREIGN KEY (vendor_id) REFERENCES _vendors(id) ON DELETE SET NULL,
    FOREIGN KEY (tax_id) REFERENCES _taxes(id) ON DELETE SET NULL,
    FOREIGN KEY (unit_id) REFERENCES _units(id) ON DELETE SET NULL,
    INDEX idx_name (name),
    INDEX idx_category (category_id)
);
```

---

#### `lumra_config_productvariants` - Product SKUs
```sql
CREATE TABLE lumra_config_productvariants (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id  BIGINT NOT NULL,  -- FK → lumra_config_products
    sku         VARCHAR(50) NOT NULL UNIQUE,
    size_weight VARCHAR(50) NULL,  -- e.g., "500g", "1L"
    price_buy   DECIMAL(12,2) NOT NULL,
    price_sell  DECIMAL(12,2) NOT NULL,
    updated_at  DATETIME AUTO_NOW,
    
    FOREIGN KEY (product_id) REFERENCES lumra_config_products(id) ON DELETE CASCADE,
    INDEX idx_sku (sku),
    INDEX idx_product (product_id)
);
```

**Example:**
```
id | product_id | sku        | size_weight | price_buy | price_sell
1  | 5          | COFFEE-500 | 500g        | 25000     | 35000
2  | 5          | COFFEE-1KG | 1kg         | 45000     | 65000
3  | 5          | COFFEE-5KG | 5kg         | 200000    | 280000
```

---

#### `lumra_config_productattribute_items` - Variant Attributes
```sql
CREATE TABLE lumra_config_productattribute_items (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    variant_id  BIGINT NOT NULL,  -- FK → lumra_config_productvariants
    attr_name   VARCHAR(100) NOT NULL,
    attr_value  VARCHAR(255) NOT NULL,
    updated_at  DATETIME AUTO_NOW,
    
    FOREIGN KEY (variant_id) REFERENCES lumra_config_productvariants(id) ON DELETE CASCADE,
    INDEX idx_variant (variant_id)
);
```

**Example:**
```
id | variant_id | attr_name  | attr_value
1  | 1          | roast_level| medium
2  | 1          | origin     | Indonesia
3  | 1          | bean_type  | arabica
4  | 2          | roast_level| dark
```

---

### 3. STOCK MANAGEMENT TABLES

#### `lumra_config_stock` - Stock Inventory
```sql
CREATE TABLE lumra_config_stock (
    id               BIGINT PRIMARY KEY AUTO_INCREMENT,
    variant_id       BIGINT NOT NULL,  -- FK → lumra_config_productvariants
    location_id      BIGINT NOT NULL,  -- FK → lumra_config_locations
    quantity         INT DEFAULT 0,
    transaction_type VARCHAR(20),  -- in, out, adjustment, transfer_sent, transfer_received
    notes            TEXT,
    last_updated     DATETIME AUTO_NOW,
    created_at       DATETIME AUTO_NOW_ADD,
    
    FOREIGN KEY (variant_id) REFERENCES lumra_config_productvariants(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES lumra_config_locations(id) ON DELETE CASCADE,
    UNIQUE KEY idx_variant_location (variant_id, location_id),
    INDEX idx_location (location_id)
);
```

---

#### `lumra_config_stockopname_session` - Physical Count Sessions
```sql
CREATE TABLE lumra_config_stockopname_session (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    location_id BIGINT NOT NULL,  -- FK → lumra_config_locations
    created_by  BIGINT NOT NULL,  -- FK → auth_user
    status      VARCHAR(20) DEFAULT 'in_progress',
    notes       TEXT,
    created_at  DATETIME AUTO_NOW_ADD,
    submitted_at DATETIME NULL,
    approved_at  DATETIME NULL,
    
    FOREIGN KEY (location_id) REFERENCES lumra_config_locations(id) ON DELETE PROTECT,
    FOREIGN KEY (created_by) REFERENCES auth_user(id) ON DELETE PROTECT,
    INDEX idx_location (location_id),
    INDEX idx_status (status)
);
```

---

#### `lumra_config_stockopname_item` - Physical Count Items
```sql
CREATE TABLE lumra_config_stockopname_item (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id    BIGINT NOT NULL,  -- FK → lumra_config_stockopname_session
    variant_id    BIGINT NOT NULL,  -- FK → lumra_config_productvariants
    current_stock INT DEFAULT 0,
    counted_qty   INT NOT NULL,
    notes         TEXT,
    created_at    DATETIME AUTO_NOW_ADD,
    
    FOREIGN KEY (session_id) REFERENCES lumra_config_stockopname_session(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES lumra_config_productvariants(id) ON DELETE PROTECT,
    UNIQUE KEY idx_session_variant (session_id, variant_id),
    INDEX idx_created_at (created_at)
);
```

---

#### `lumra_config_supplier_prices` - Vendor Pricing
```sql
CREATE TABLE lumra_config_supplier_prices (
    id               BIGINT PRIMARY KEY AUTO_INCREMENT,
    vendor_id        BIGINT NOT NULL,  -- FK → _vendors
    variant_id       BIGINT NOT NULL,  -- FK → lumra_config_productvariants
    unit_price       DECIMAL(12,2) NOT NULL,
    currency         VARCHAR(3) DEFAULT 'IDR',
    minimum_quantity INT DEFAULT 1,
    maximum_quantity INT NULL,
    lead_time_days   INT DEFAULT 0,
    is_active        BOOLEAN DEFAULT TRUE,
    is_preferred     BOOLEAN DEFAULT FALSE,
    last_updated_by  BIGINT NULL,  -- FK → auth_user
    effective_date   DATE NULL,
    valid_until      DATE NULL,
    created_at       DATETIME AUTO_NOW_ADD,
    updated_at       DATETIME AUTO_NOW,
    
    FOREIGN KEY (vendor_id) REFERENCES _vendors(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES lumra_config_productvariants(id) ON DELETE CASCADE,
    FOREIGN KEY (last_updated_by) REFERENCES auth_user(id) ON DELETE SET NULL,
    UNIQUE KEY idx_vendor_variant (vendor_id, variant_id),
    INDEX idx_is_preferred (is_preferred),
    INDEX idx_valid_until (valid_until)
);
```

---

### 4. WORKFLOW TABLES

#### `lumra_config_requisitions` - Stock Requisitions
```sql
CREATE TABLE lumra_config_requisitions (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    from_location_id BIGINT NOT NULL,  -- FK → lumra_config_locations
    to_location_id   BIGINT NOT NULL,  -- FK → lumra_config_locations
    requested_by  BIGINT NOT NULL,  -- FK → auth_user
    approved_by   BIGINT NULL,  -- FK → auth_user
    status        VARCHAR(20) DEFAULT 'waiting',  -- waiting, approved, in_transit, completed, rejected
    created_at    DATETIME AUTO_NOW_ADD,
    approved_at   DATETIME NULL,
    
    FOREIGN KEY (from_location_id) REFERENCES lumra_config_locations(id) ON DELETE CASCADE,
    FOREIGN KEY (to_location_id) REFERENCES lumra_config_locations(id) ON DELETE CASCADE,
    FOREIGN KEY (requested_by) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES auth_user(id) ON DELETE SET NULL,
    INDEX idx_from_location (from_location_id),
    INDEX idx_to_location (to_location_id),
    INDEX idx_status (status)
);
```

---

#### `lumra_config_transfers` - Stock Transfers
```sql
CREATE TABLE lumra_config_transfers (
    id                      BIGINT PRIMARY KEY AUTO_INCREMENT,
    requisition_id          BIGINT NULL,  -- FK → lumra_config_requisitions
    source_location_id      BIGINT NOT NULL,  -- FK → lumra_config_locations
    destination_location_id BIGINT NOT NULL,  -- FK → lumra_config_locations
    created_by              BIGINT NOT NULL,  -- FK → auth_user
    status                  VARCHAR(20) DEFAULT 'pending',  -- pending, in_transit, received, cancelled
    notes                   TEXT,
    created_at              DATETIME AUTO_NOW_ADD,
    sent_at                 DATETIME NULL,
    received_at             DATETIME NULL,
    
    FOREIGN KEY (requisition_id) REFERENCES lumra_config_requisitions(id) ON DELETE CASCADE,
    FOREIGN KEY (source_location_id) REFERENCES lumra_config_locations(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_location_id) REFERENCES lumra_config_locations(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES auth_user(id) ON DELETE CASCADE,
    INDEX idx_source (source_location_id),
    INDEX idx_destination (destination_location_id),
    INDEX idx_status (status)
);
```

---

### 5. ORDER TABLES

#### `lumra_config_orders` - Sales Orders/Transactions
```sql
CREATE TABLE lumra_config_orders (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id   BIGINT NULL,  -- FK → lumra_config_customers
    customer_name VARCHAR(100) NOT NULL,  -- for backward compatibility
    status        VARCHAR(20) DEFAULT 'pending',  -- pending, completed, cancelled
    created_at    DATETIME DEFAULT NOW(),
    
    FOREIGN KEY (customer_id) REFERENCES lumra_config_customers(id) ON DELETE SET NULL,
    INDEX idx_customer (customer_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

---

#### `lumra_config_orderitems` - Order Line Items
```sql
CREATE TABLE lumra_config_orderitems (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id    BIGINT NOT NULL,  -- FK → lumra_config_orders
    variant_id  BIGINT NOT NULL,  -- FK → lumra_config_productvariants
    quantity    INT DEFAULT 1,
    price       DECIMAL(12,2) NOT NULL,  -- price at time of sale (snapshot)
    
    FOREIGN KEY (order_id) REFERENCES lumra_config_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES lumra_config_productvariants(id) ON DELETE PROTECT,
    INDEX idx_order (order_id),
    INDEX idx_variant (variant_id)
);
```

**Note:** `total_price` calculated via ORM aggregation: `Sum(quantity * price)`

---

### 6. PRODUCTION TABLES

#### `production_recipe_categories` - Recipe Classifications
```sql
CREATE TABLE production_recipe_categories (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  DATETIME AUTO_NOW_ADD,
    updated_at  DATETIME AUTO_NOW,
    
    INDEX idx_name (name)
);
```

---

#### `production_recipes` - Recipes/Formulas
```sql
CREATE TABLE production_recipes (
    id               BIGINT PRIMARY KEY AUTO_INCREMENT,
    name             VARCHAR(255) NOT NULL UNIQUE,
    description      TEXT,
    instructions     TEXT,
    category_id      BIGINT NULL,  -- FK → production_recipe_categories
    yield_quantity   DECIMAL(12,2) DEFAULT 1,
    yield_unit_id    BIGINT NULL,  -- FK → _units
    preparation_time INT DEFAULT 5,  -- minutes
    total_cost       DECIMAL(12,2) DEFAULT 0,  -- calculated from ingredients
    cost_per_unit    DECIMAL(12,2) DEFAULT 0,  -- total_cost / yield_quantity
    is_archived      BOOLEAN DEFAULT FALSE,
    created_at       DATETIME AUTO_NOW_ADD,
    updated_at       DATETIME AUTO_NOW,
    
    FOREIGN KEY (category_id) REFERENCES production_recipe_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (yield_unit_id) REFERENCES _units(id) ON DELETE SET NULL,
    INDEX idx_name (name),
    INDEX idx_category (category_id)
);
```

---

#### `production_recipe_ingredients` - Recipe Ingredients
```sql
CREATE TABLE production_recipe_ingredients (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    recipe_id     BIGINT NOT NULL,  -- FK → production_recipes
    variant_id    BIGINT NOT NULL,  -- FK → lumra_config_productvariants
    quantity      DECIMAL(12,2) NOT NULL,
    unit_id       BIGINT NULL,  -- FK → _units
    unit_cost     DECIMAL(12,2) DEFAULT 0,  -- snapshot of variant.price_buy at save time
    subtotal_cost DECIMAL(12,2) DEFAULT 0,  -- quantity * unit_cost
    notes         TEXT,
    created_at    DATETIME AUTO_NOW_ADD,
    
    FOREIGN KEY (recipe_id) REFERENCES production_recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES lumra_config_productvariants(id) ON DELETE PROTECT,
    FOREIGN KEY (unit_id) REFERENCES _units(id) ON DELETE SET NULL,
    UNIQUE KEY idx_recipe_variant (recipe_id, variant_id),
    INDEX idx_recipe (recipe_id)
);
```

---

### 7. USER TABLES

#### `lumra_config_userprofile` - User Extensions
```sql
CREATE TABLE lumra_config_userprofile (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id     BIGINT NOT NULL UNIQUE,  -- FK → auth_user (OneToOne)
    location_id BIGINT NULL,  -- FK → lumra_config_locations
    
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES lumra_config_locations(id) ON DELETE SET NULL
);
```

---

### 8. TARGET TABLES

#### `lumra_config_sales_targets` - Sales Targets
```sql
CREATE TABLE lumra_config_sales_targets (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    year          INT NOT NULL,
    month         INT NOT NULL,  -- 1-12
    target_amount DECIMAL(15,2) NOT NULL,
    notes         TEXT,
    created_by    BIGINT NULL,  -- FK → auth_user
    created_at    DATETIME AUTO_NOW_ADD,
    updated_at    DATETIME AUTO_NOW,
    
    FOREIGN KEY (created_by) REFERENCES auth_user(id) ON DELETE SET NULL,
    UNIQUE KEY idx_year_month (year, month),
    INDEX idx_created_by (created_by)
);
```

---

### 9. DATABASE VIEWS

#### `product_details_view` - Denormalized Product View
```sql
CREATE VIEW product_details_view AS
SELECT 
    pv.sku,
    p.name,
    pv.price_buy,
    pv.price_sell,
    pa_bean.attr_value AS bean_type,
    pa_tag.attr_value AS tag,
    pa_roast.attr_value AS roast_level,
    pa_proc.attr_value AS processing,
    c.name AS category,
    p.description
FROM lumra_config_productvariants pv
LEFT JOIN lumra_config_products p ON pv.product_id = p.id
LEFT JOIN _categories c ON p.category_id = c.id
LEFT JOIN lumra_config_productattribute_items pa_bean 
    ON pv.id = pa_bean.variant_id AND pa_bean.attr_name = 'bean_type'
LEFT JOIN lumra_config_productattribute_items pa_tag 
    ON pv.id = pa_tag.variant_id AND pa_tag.attr_name = 'tag'
LEFT JOIN lumra_config_productattribute_items pa_roast 
    ON pv.id = pa_roast.variant_id AND pa_roast.attr_name = 'roast_level'
LEFT JOIN lumra_config_productattribute_items pa_proc 
    ON pv.id = pa_proc.variant_id AND pa_proc.attr_name = 'processing';
```

**Note:** This is a read-only database view (Django model with `managed=False`)

---

## 🔗 Foreign Key Relationships

### Complete Relationship Map

| Source Table | Source Field | Target Table | Target Field | Constraint | Cascade |
|---|---|---|---|---|---|
| lumra_config_products | category_id | _categories | id | NOT NULL | SET NULL |
| lumra_config_products | vendor_id | _vendors | id | NOT NULL | SET NULL |
| lumra_config_products | tax_id | _taxes | id | NOT NULL | SET NULL |
| lumra_config_products | unit_id | _units | id | NOT NULL | SET NULL |
| lumra_config_productvariants | product_id | lumra_config_products | id | NOT NULL | CASCADE |
| lumra_config_productattribute_items | variant_id | lumra_config_productvariants | id | NOT NULL | CASCADE |
| lumra_config_stock | variant_id | lumra_config_productvariants | id | NOT NULL | CASCADE |
| lumra_config_stock | location_id | lumra_config_locations | id | NOT NULL | CASCADE |
| lumra_config_stockopname_session | location_id | lumra_config_locations | id | NOT NULL | PROTECT |
| lumra_config_stockopname_session | created_by | auth_user | id | NOT NULL | PROTECT |
| lumra_config_stockopname_item | session_id | lumra_config_stockopname_session | id | NOT NULL | CASCADE |
| lumra_config_stockopname_item | variant_id | lumra_config_productvariants | id | NOT NULL | PROTECT |
| lumra_config_requisitions | from_location_id | lumra_config_locations | id | NOT NULL | CASCADE |
| lumra_config_requisitions | to_location_id | lumra_config_locations | id | NOT NULL | CASCADE |
| lumra_config_requisitions | requested_by | auth_user | id | NOT NULL | CASCADE |
| lumra_config_requisitions | approved_by | auth_user | id | NULL | SET NULL |
| lumra_config_requisitionitem | requisition_id | lumra_config_requisitions | id | NOT NULL | CASCADE |
| lumra_config_requisitionitem | variant_id | lumra_config_productvariants | id | NOT NULL | PROTECT |
| lumra_config_transfers | requisition_id | lumra_config_requisitions | id | NULL | CASCADE |
| lumra_config_transfers | source_location_id | lumra_config_locations | id | NOT NULL | CASCADE |
| lumra_config_transfers | destination_location_id | lumra_config_locations | id | NOT NULL | CASCADE |
| lumra_config_transfers | created_by | auth_user | id | NOT NULL | CASCADE |
| lumra_config_transferitem | transfer_id | lumra_config_transfers | id | NOT NULL | CASCADE |
| lumra_config_transferitem | variant_id | lumra_config_productvariants | id | NOT NULL | PROTECT |
| lumra_config_orders | customer_id | lumra_config_customers | id | NULL | SET NULL |
| lumra_config_orderitems | order_id | lumra_config_orders | id | NOT NULL | CASCADE |
| lumra_config_orderitems | variant_id | lumra_config_productvariants | id | NOT NULL | PROTECT |
| lumra_config_supplier_prices | vendor_id | _vendors | id | NOT NULL | CASCADE |
| lumra_config_supplier_prices | variant_id | lumra_config_productvariants | id | NOT NULL | CASCADE |
| lumra_config_supplier_prices | last_updated_by | auth_user | id | NULL | SET NULL |
| production_recipes | category_id | production_recipe_categories | id | NULL | SET NULL |
| production_recipes | yield_unit_id | _units | id | NULL | SET NULL |
| production_recipe_ingredients | recipe_id | production_recipes | id | NOT NULL | CASCADE |
| production_recipe_ingredients | variant_id | lumra_config_productvariants | id | NOT NULL | PROTECT |
| production_recipe_ingredients | unit_id | _units | id | NULL | SET NULL |
| lumra_config_userprofile | user_id | auth_user | id | NOT NULL | CASCADE |
| lumra_config_userprofile | location_id | lumra_config_locations | id | NULL | SET NULL |
| lumra_config_sales_targets | created_by | auth_user | id | NULL | SET NULL |

---

## 🔑 Unique Constraints

| Table | Constraint | Fields | Purpose |
|-------|-----------|--------|---------|
| _categories | UNIQUE | name | Prevent duplicate category names |
| _categories | UNIQUE | slug | Prevent duplicate URL slugs |
| _units | UNIQUE | name | Prevent duplicate unit names |
| _vendors | UNIQUE | name | Prevent duplicate vendor names |
| _taxes | UNIQUE | name | Prevent duplicate tax names |
| lumra_config_locations | UNIQUE | name | Prevent duplicate locations |
| lumra_config_customers | UNIQUE | email | Prevent duplicate customer emails |
| lumra_config_productvariants | UNIQUE | sku | Prevent duplicate SKUs |
| lumra_config_stockopname_item | UNIQUE | (session_id, variant_id) | One count per product per session |
| lumra_config_requisitionitem | UNIQUE | (requisition_id, variant_id) | One line per requisition |
| lumra_config_supplier_prices | UNIQUE | (vendor_id, variant_id) | One price per vendor-product combo |
| production_recipes | UNIQUE | name | Prevent duplicate recipe names |
| production_recipe_ingredients | UNIQUE | (recipe_id, variant_id) | One ingredient per recipe |
| lumra_config_userprofile | UNIQUE | user_id | One profile per user (OneToOne) |
| lumra_config_sales_targets | UNIQUE | (year, month) | One target per month |

---

## 📇 Indexes

| Table | Index | Fields | Type | Purpose |
|-------|-------|--------|------|---------|
| _categories | idx_name | name | BTREE | Fast category lookup by name |
| _categories | idx_slug | slug | BTREE | Fast category lookup by slug |
| _units | idx_name | name | BTREE | Fast unit lookup |
| _vendors | idx_name | name | BTREE | Fast vendor lookup |
| _vendors | idx_email | email | BTREE | Fast vendor lookup by email |
| _taxes | idx_name | name | BTREE | Fast tax lookup |
| lumra_config_locations | idx_name | name | BTREE | Fast location lookup |
| lumra_config_customers | idx_name | name | BTREE | Fast customer search |
| lumra_config_customers | idx_email | email | BTREE | Fast customer lookup by email |
| lumra_config_customers | idx_tier | tier | BTREE | Loyalty tier filtering |
| lumra_config_products | idx_name | name | BTREE | Product search |
| lumra_config_products | idx_category | category_id | BTREE | Products by category |
| lumra_config_productvariants | idx_sku | sku | BTREE | SKU lookup (critical) |
| lumra_config_productvariants | idx_product | product_id | BTREE | Variants by product |
| lumra_config_stock | idx_variant_location | (variant_id, location_id) | BTREE | Stock lookup (composite) |
| lumra_config_stock | idx_location | location_id | BTREE | Stock by location |
| lumra_config_stockopname_session | idx_location | location_id | BTREE | Opname sessions by location |
| lumra_config_stockopname_session | idx_status | status | BTREE | Opname filtering |
| lumra_config_orders | idx_customer | customer_id | BTREE | Orders by customer |
| lumra_config_orders | idx_status | status | BTREE | Order filtering |
| lumra_config_orders | idx_created_at | created_at | BTREE | Time-based queries |
| lumra_config_supplier_prices | idx_is_preferred | is_preferred | BTREE | Preferred supplier filtering |
| lumra_config_supplier_prices | idx_valid_until | valid_until | BTREE | Price validity |
| production_recipes | idx_name | name | BTREE | Recipe lookup |
| production_recipes | idx_category | category_id | BTREE | Recipes by category |
| _categories | idx_parent_category | parent_id | BTREE | Category hierarchy traversal |

---

## 📊 Data Types Reference

| Django Type | SQL Type | Size | Use Case |
|---|---|---|---|
| `AutoField` | BIGINT | 8 bytes | Primary keys (max ~9.2×10^18) |
| `CharField(n)` | VARCHAR(n) | n bytes | Short text (names, codes) |
| `TextField` | LONGTEXT | Up to 4GB | Long text (descriptions, notes) |
| `IntegerField` | INT | 4 bytes | Whole numbers (-2B to +2B) |
| `PositiveIntegerField` | INT | 4 bytes | Non-negative integers |
| `DecimalField(a,b)` | DECIMAL(a,b) | Variable | Money, prices (12,2 = max 999,999,999.99) |
| `BooleanField` | TINYINT(1) | 1 byte | True/False |
| `DateField` | DATE | 3 bytes | Calendar dates |
| `DateTimeField` | DATETIME | 8 bytes | Timestamps with time |
| `EmailField` | VARCHAR(100) | 100 bytes | Email addresses (unique constrained) |
| `URLField` | VARCHAR(255) | 255 bytes | URLs |
| `ForeignKey` | BIGINT | 8 bytes | References to other tables |
| `OneToOneField` | BIGINT | 8 bytes | One-to-one relationships |

---

## ✅ Validation Rules

### Required Fields (NOT NULL)

```
MASTER DATA:
- Category: name
- Unit: name
- Vendor: name
- Tax: name, rate
- Location: name

PRODUCTS:
- Product: name
- ProductVariant: product_id, sku, price_buy, price_sell
- ProductAttribute: variant_id, attr_name, attr_value

STOCK:
- Stock: variant_id, location_id, quantity, transaction_type
- StockOpnameSession: location_id, created_by
- StockOpnameItem: session_id, variant_id, counted_qty

ORDERS:
- Order: status, created_at
- OrderItem: order_id, variant_id, quantity, price

RECIPES:
- Recipe: name
- RecipeIngredient: recipe_id, variant_id, quantity

WORKFLOW:
- Requisition: from_location_id, to_location_id, requested_by
- Transfer: source_location_id, destination_location_id, created_by
```

### Unique Validations

```
NATURAL KEYS (Business unique identifiers):
- Category.name
- Unit.name
- Vendor.name
- Tax.name
- Location.name
- Customer.email
- ProductVariant.sku
- Production.Recipe.name
- SalesTarget (year, month) combination
```

### Field Constraints

```
DECIMAL FIELDS (Money/Pricing):
- price_buy, price_sell, unit_price: DECIMAL(12,2)
  Max value: 999,999,999.99 (10 million rupiah)
  Min value: 0.00
  Precision: 2 decimal places

- total_cost, cost_per_unit: DECIMAL(12,2)
  Calculated from ingredients, stored for performance

- target_amount: DECIMAL(15,2)
  Max value: 999,999,999,999.99 (1 trillion rupiah)

CHOICE FIELDS (Enums):
- Customer.tier: 'bronze', 'silver', 'gold', 'platinum'
- Stock.transaction_type: 'in', 'out', 'adjustment', 'transfer_sent', 'transfer_received'
- Requisition.status: 'waiting', 'approved', 'in_transit', 'completed', 'rejected'
- Transfer.status: 'pending', 'in_transit', 'received', 'cancelled'
- Order.status: 'pending', 'completed', 'cancelled'
- StockOpnameSession.status: 'in_progress', 'submitted', 'approved', 'rejected'
- SalesTarget.month: 1-12 (January-December)
```

---

## 🔄 Workflow Models

### Stock Opname Workflow States

```
StockOpnameSession States:
- in_progress      → Staff counting items
- submitted        → Pending manager approval
- approved         → Applied to inventory, Stock records updated
- rejected         → Sent back to staff for recount

StockOpnameItem:
- current_stock    = Stock.quantity at session start
- counted_qty      = Physical count by staff
- difference       = counted_qty - current_stock (calculated property)
- is_accurate      = (difference == 0) (calculated property)
```

### Requisition Workflow States

```
Requisition States:
- waiting          → Pending approval
- approved         → Approved, Transfer object created
- in_transit       → Packed and sent
- completed        → Received and verified
- rejected         → Approval denied

Transfer States (derived from Requisition):
- pending          → Created, awaiting packing
- in_transit       → Sent from source
- received         → Received at destination
- cancelled        → Order cancelled
```

### Order Workflow States

```
Order States:
- pending          → Created (POS transactions → completed immediately)
- completed        → Sold, revenue recognized
- cancelled        → Transaction voided/refunded
```

---

## 📈 Data Growth Estimates (1 Year, Medium Store)

```
MASTER DATA (static):
- Categories: 50
- Units: 10
- Vendors: 20
- Tax rates: 5
- Locations: 3

PRODUCTS:
- Products: 500
- ProductVariants (SKUs): 1,000
- ProductAttributes: 2,000

TRANSACTIONAL (daily):
- Orders (transactions): 50/day × 365 = 18,250
- OrderItems: 100,000
- Stock movements: 20/day × 365 = 7,300
- Stock entries (stock level snapshots): ~3,000

CUSTOMERS:
- Customer records: 1,000
- Orders per customer: ~18 avg

REPORTS (monthly):
- SalesTarget: 12/year = 12
- Requisitions: 10/month × 12 = 120
- Transfers: 40/month × 12 = 480

Total rows estimate: ~125,000 rows for 1 year

Database size estimate:
- With indexes: 500-800 MB
- With full transaction history: 1-2 GB
```

---

## 🔐 Data Integrity Rules

### Cascade Delete Rules

| Action | Behavior | Why |
|--------|----------|-----|
| Delete Category | Products set category_id → NULL | Category is reference data, don't lose products |
| Delete Product | ProductVariants CASCADE DELETE | Variants only exist under product |
| Delete ProductVariant | Remove from Stock, Orders, Recipes | Variant lifecycle ends |
| Delete Location | Stock, Transfers CASCADE DELETE | Location stock irrelevant after deletion |
| Delete User | Transfer via ON DELETE CASCADE | Preserve audit trail |
| Delete Recipe | RecipeIngredients CASCADE DELETE | Ingredients only exist under recipe |

### Protect Constraints

| Action | Behavior | Why |
|--------|----------|-----|
| Delete ProductVariant | → reject if in Requisition | Audit trail integrity |
| Delete ProductVariant | → reject if in StockOpnameItem | Physical count evidence |
| Delete Location | → reject if has Opname session | Can't delete location with open counts |
| Delete User | → reject if created Opname | Audit trail protection |

---

## 📝 Migration Notes

When creating migrations:

```bash
# Create initial migrations
python manage.py makemigrations lumra_config

# Apply to database
python manage.py migrate lumra_config

# Check status
python manage.py showmigrations lumra_config

# Squash migrations (consolidate history)
python manage.py squashmigrations lumra_config 0001 0015

# Reverse migration (if needed)
python manage.py migrate lumra_config 0010  # Go back to migration 0010
```

---

## 🔍 Performance Tips

### Query Optimization

```python
# ❌ N+1 Problem - will do 1001 queries
products = Product.objects.all()
for product in products:
    print(product.category.name)  # 1 query per product

# ✅ Fixed with select_related (1 query for 1000 products)
products = Product.objects.select_related('category').all()

# ❌ For aggregations - calculate in Python (bad)
for product in products:
    total_stock = sum([s.quantity for s in product.variants.stock_entries.all()])

# ✅ Use ORM aggregation (1 query)
from django.db.models import Sum
variants = ProductVariant.objects.filter(product_id=product.id).aggregate(
    total_stock=Sum('stock_entries__quantity')
)
```

### Index Strategy

```
Critical indexes (must exist):
- ProductVariant.sku (SKU lookup is frequent)
- Order.created_at (time range queries)
- Stock (variant_id, location_id) composite
- Customer.email (lookup during POS)

Consider if performance issue:
- Requisition.status (if many pending requisitions)
- Transfer.status (if many transfers)
```

---

**This database schema supports ~50 concurrent users with medium transaction volume.**
