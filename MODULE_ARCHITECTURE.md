# 🎯 LUMRA ERP - Module Architecture & System Overview
**Complete System Architecture with Module Interconnections**  
*Generated: April 10, 2026*

---

## 📑 Table of Contents
1. [System Architecture](#system-architecture)
2. [10 Core Business Modules](#10-core-business-modules)
3. [Module Dependencies](#module-dependencies)
4. [Data Relationships](#data-relationships)
5. [User Role Access Matrix](#user-role-access-matrix)
6. [Process Workflows](#process-workflows)
7. [Implementation Guide](#implementation-guide)

---

## 🏗️ System Architecture

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│             PRESENTATION LAYER (Templates)              │
│  102 HTML files organized into 11 categories            │
│  Theme: Emerald Odyssey (Tailwind + Alpine.js)          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│             APPLICATION LAYER (Django Views)            │
│  Views split across specialized modules:                │
│  - inventory_views.py, sales_views.py, etc.             │
│  - Handles business logic & data aggregation            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│             DATA LAYER (Django Models)                  │
│  Core tables:                                           │
│  - Product, Category, Unit, Vendor                      │
│  - StockMovement, StockOpname, Location                 │
│  - Customer, Transaction, OrderItem                     │
│  - Campaign, Discount, LoyaltyMember                    │
│  - UserRole, Permission                                │
└─────────────────────────────────────────────────────────┘
```

### System Features
- **Authentication**: Role-based access control (RBAC)
- **Responsive Design**: Mobile-first, works on all devices
- **Real-time Updates**: Alpine.js for instant feedback
- **Audit Trail**: Activity logging for compliance
- **Multi-location**: Support for multiple stores/warehouses
- **Reporting**: 20+ pre-built reports with export

---

## 📦 10 Core Business Modules

### 1️⃣ AUTH & USERS MODULE
**Purpose:** System access control  
**Templates:** 2 files
```
auth/
├── login.html          → User authentication
└── register.html       → New user account creation

settings/
├── users.html          → User management
├── profile.html        → Personal profile
├── user_roles_permissions.html  (referenced)
└── business_feature_matrix.html → Feature licensing
```

**Key Features:**
- Login/Logout
- Role-based access (Admin, Manager, Staff, Viewer)
- Password management
- Two-factor authentication setup
- Activity audit trail

**Related Views:** `auth_views.py`  
**Data Model:** User, Role, Permission, ActivityLog

---

### 2️⃣ INVENTORY MANAGEMENT MODULE
**Purpose:** Stock & supply chain management  
**Templates:** 16 files
```
inventory/
├── products.html                 → Product listing
├── product_list.html             → Alternative product view
├── product_details.html          → Product detail
├── stock_overview.html           → Stock dashboard
├── stock_movement.html           → Stock transaction log
├── add_stock_movement.html       → Create stock movement
├── stock_planning.html           → Stock allocation
├── stock_opname_locations.html   → Location selection
├── stock_opname_form.html        → Physical count entry
├── stock_opname_approvals.html   → Count approval list
├── stock_opname_approval_detail.html → Approval workflow
├── stock_purchasing.html         → Purchase orders
├── supplier_price_list.html      → Vendor pricing
├── supplier_price_form.html      → Add/edit price
└── supplier_price_confirm_delete.html → Confirm delete
```

**Key Features:**
- Product catalog management
- Stock level monitoring
- Stock opname (physical count) workflow
- Purchase order management
- Supplier price tracking
- Stock transfer between locations
- Low stock alerts

**Related Views:** `inventory_views.py`, `stock_movement_views.py`, `stock_opname_views.py`, `pricing_views.py`  
**Data Models:** Product, StockMovement, StockOpname, PurchaseOrder, SupplierPrice, Vendor

---

### 3️⃣ SALES & POS MODULE
**Purpose:** Point of sale & transaction processing  
**Templates:** 7 files
```
sales_insight/
├── pos.html                → POS interface
├── dashboard.html          → Sales dashboard with KPIs
├── sales_intelligence.html → Sales analytics
├── sales_performance.html  → Performance metrics
├── financial_reports.html  → Financial overview
├── market_insights.html    → Market analysis
└── trends_analysis.html    → Trend analysis
```

**Key Features:**
- Real-time POS transactions
- Shopping cart with dynamic totals
- Customer lookup & loyalty points
- Discount application
- Multiple payment methods
- Sales analytics & KPIs
- Daily/weekly/monthly reporting
- Financial dashboard

**Related Views:** `sales_views.py`, `misc_views.py`, `pos_views.py`  
**Data Models:** Transaction, TransactionItem, Customer, Discount, PaymentMethod

---

### 4️⃣ PRODUCTION/RECIPES MODULE
**Purpose:** Recipe & manufacturing management  
**Templates:** 3 files
```
production/
├── recipe_list.html          → Recipe catalog
├── recipe_form.html          → Create/edit recipe
└── recipe_detail.html        → Recipe details
```

**Key Features:**
- Recipe creation & management
- Ingredient list with quantities
- Cost auto-calculation
- Yield specification
- Recipe usage tracking
- COGS calculation support

**Related Views:** `production_views.py`  
**Data Models:** Recipe, RecipeIngredient

---

### 5️⃣ MARKETING & LOYALTY MODULE
**Purpose:** Campaigns, discounts, and loyalty programs  
**Templates:** 5 files
```
marketing/
├── campaign.html           → Campaign list
├── campaign_list.html      → Alternative campaign view
├── add_campaign.html       → Create campaign
├── discount.html           → Discount management
└── loyalty_members.html    → Loyalty member list
```

**Key Features:**
- Campaign planning & execution
- Promotional discounts
- Loyalty points system
- Member tier management
- Campaign performance tracking
- Redemption management

**Related Views:** `misc_views.py` (marketing functions)  
**Data Models:** Campaign, Discount, LoyaltyMember, LoyaltyPoints

---

### 6️⃣ MASTER DATA MODULE
**Purpose:** Core reference data management  
**Templates:** 13 files
```
master_data/
├── categories_list.html         → Product categories
├── category_form.html           → Create/edit category
├── units_list.html              → Units of measurement
├── unit_form.html               → Create/edit unit
├── vendors_list.html            → Vendor/supplier list
├── vendor_list.html             → Alternative vendor view
├── vendor_form.html             → Create/edit vendor
├── customers.html               → Customer dashboard
├── customers_list.html          → Customer list
├── customer_detail.html         → Customer profile
├── customer_form.html           → Create/edit customer
├── locations.html               → Store locations
├── location_list.html           → Location inventory
└── stock_opname_session_detail.html → Historical stock count
```

**Key Features:**
- Product category hierarchy
- Unit of measurement definition
- Vendor/supplier management
- Customer database
- Store/location management
- Tax rate setting

**Related Views:** `masterdata_views.py`, `customer_views.py`  
**Data Models:** Category, Unit, Vendor, Customer, Location, Tax

---

### 7️⃣ REPORTS & ANALYTICS MODULE
**Purpose:** Business intelligence & reporting  
**Templates:** 20 files
```
reports/
├── reporting.html                  → Report hub
├── base_report.html                → Report template base
├── sales_report.html               → Sales analysis
├── sales_history.html              → Transaction history
├── sales_history_product.html      → Sales by product
├── report_sales_by_outlet.html     → Sales by location
├── report_sales_by_payment.html    → Payment breakdown
├── report_sales_by_product.html    → Product performance
├── report_sales_summary.html       → Sales summary
├── report_sales_after.html         → Enhanced sales report
├── report_inventory_stock.html     → Stock levels
├── report_inventory_log.html       → Stock transaction log
├── report_inventory_low.html       → Low stock alert
├── report_profit_loss_detail.html  → P&L statement
├── requisition_report.html         → Requisition tracking
├── purchasing_report.html          → Purchase order tracking
├── transfer_report.html            → Stock transfer report
├── transaction_summary.html        → Daily transaction summary
├── activity_log.html               → User activity audit
└── sales_report_after.html         → Alternative sales report
```

**Key Features:**
- Sales analysis (by product, location, payment, category)
- Inventory reports (stock levels, movements, low stock)
- Financial reports (P&L, revenue, costs)
- Operational reports (requisitions, PO, transfers)
- Activity audit trails
- Data export (PDF, Excel, CSV)
- Custom date ranges & filters
- Trend analysis

**Related Views:** `report_views.py`  
**Data Models:** All (aggregated data)

---

### 8️⃣ MESSAGES & NOTIFICATIONS MODULE
**Purpose:** Internal messaging & alerts  
**Templates:** 2 files
```
messages/
├── inbox.html          → User message inbox
└── notification.html   → Notification center
```

**Key Features:**
- Internal messaging system
- Real-time notifications
- Alert types (approval, low stock, etc.)
- Message threading
- Read/unread status
- Push notifications (optional)

**Related Views:** `notification_views.py` (referenced)  
**Data Models:** Message, Notification, NotificationPreference

---

### 9️⃣ SETTINGS & ADMIN MODULE
**Purpose:** System configuration & administration  
**Templates:** 10 files
```
settings/
├── settings.html                  → Settings hub
├── profile.html                   → User profile
├── users.html                     → User management
├── business_settings.html         → Business config hub
├── business_form_general.html     → Business info form
├── business_profile.html          → Business profile view
├── business_feature_matrix.html   → Feature enablement
├── system_status.html             → System health
├── about.html                     → About system
├── contact.html                   → Support/contact
└── search.html                    → Global search
```

**Key Features:**
- Business information management
- Logo/branding upload
- System configuration (currency, timezone, etc.)
- User management & roles
- Feature activation/licensing
- System health monitoring
- Backup & restore
- Data export

**Related Views:** `settings_views.py`, `admin_views.py`  
**Data Models:** BusinessProfile, SystemSetting, Backup

---

### 🔟 ERROR HANDLING MODULE
**Purpose:** User-friendly error pages  
**Templates:** 3 files
```
etc/
├── error_403.html      → Access denied
├── error_404.html      → Page not found
└── error_500.html      → Server error
```

**Features:**
- Helpful error messages
- Suggested actions (go home, report, retry)
- Contact support information
- Navigation hints

---

## 🔗 Module Dependencies

### Dependency Graph
```
┌─ REPORTS (20 templates)
│  ↓
│  Consumes data from: SALES, INVENTORY, MASTER DATA
│
├─ SALES (7 templates)
│  ├─ Uses: INVENTORY (products), MASTER DATA (customers)
│  ├─ Uses: MARKETING (discounts)
│  └─ Feeds to: REPORTS
│
├─ INVENTORY (16 templates)
│  ├─ Uses: MASTER DATA (products, categories, vendors, locations)
│  ├─ Uses: PRODUCTION (recipes - for COGS)
│  └─ Feeds to: REPORTS, SALES
│
├─ MASTER DATA (13 templates)
│  ├─ Core data used by: SALES, INVENTORY, MARKETING, PRODUCTION
│  └─ Indirect feed to: REPORTS
│
├─ PRODUCTION (3 templates)
│  ├─ Uses: INVENTORY (products)
│  └─ Feeds to: INVENTORY (for COGS)
│
├─ MARKETING (5 templates)
│  ├─ Uses: MASTER DATA (customers)
│  └─ Feeds to: SALES (discounts at POS)
│
├─ SETTINGS (10 templates)
│  ├─ Auth: Controls access to all modules
│  └─ Config: Used by all modules
│
├─ MESSAGES (2 templates)
│  └─ Used by: All modules (notifications)
│
├─ AUTH (2 templates)
│  └─ Gate: All modules require login
│
└─ ERROR (3 templates)
   └─ Displayed by: All modules on error
```

### Data Flow
```
POS Transaction Flow:
auth/login.html → sales_insight/pos.html
                    ├─ queries: inventory/products
                    ├─ queries: master_data/customers
                    ├─ applies: marketing/discount
                    └─ saves → reports/sales_history.html
                                → sales_insight/dashboard.html
                                → reports/transaction_summary.html

Stock Movement Flow:
inventory/products.html → inventory/stock_overview.html
                            └─ low stock? → inventory/add_stock_movement.html
                                             → inventory/stock_movement.html
                                             → reports/report_inventory_low.html

Purchase Order Flow:
inventory/stock_purchasing.html ← linked to master_data/vendors_list.html
                                    → reports/purchasing_report.html
                                    → inventory/stock_movement.html (receive goods)

Stock Opname Flow:
inventory/stock_opname_locations.html
  → inventory/stock_opname_form.html (count)
  → inventory/stock_opname_approvals.html (review)
  → inventory/stock_opname_approval_detail.html (detail approval)
  → inventory/stock_movement.html (create adjustment)
  → master_data/stock_opname_session_detail.html (history)
```

---

## 🗄️ Data Relationships

### Core Data Models & Their Templates

```
PRODUCT
├─ Created/edited in: inventory/products.html
├─ Details: inventory/product_details.html
├─ Category: master_data/categories_list.html
├─ Unit: master_data/units_list.html
├─ Used in: 
│  ├─ sales_insight/pos.html (POS)
│  ├─ inventory/stock_movement.html (stock)
│  ├─ production/recipe_detail.html (recipes)
│  └─ reports/report_sales_by_product.html
└─ Foreign Keys:
   ├─ category_id → Category
   └─ unit_id → Unit

CUSTOMER
├─ Created/edited in: master_data/customer_form.html
├─ Listed in: master_data/customers_list.html
├─ Details: master_data/customer_detail.html
├─ Used in:
│  ├─ sales_insight/pos.html (customer lookup)
│  └─ reports/sales_history.html (transaction viewer)
└─ Foreign Keys:
   └─ loyalty_tier → LoyaltyTier

TRANSACTION
├─ Created in: sales_insight/pos.html
├─ Listed in: reports/sales_history.html
├─ Breakdown: reports/report_sales_by_product.html
├─ Analytics: sales_insight/sales_intelligence.html
├─ KPI display: sales_insight/dashboard.html
└─ Foreign Keys:
   ├─ customer_id → Customer
   ├─ location_id → Location
   └─ payment_method → PaymentMethod

STOCK_MOVEMENT
├─ Created in: inventory/add_stock_movement.html
├─ Listed in: inventory/stock_movement.html
├─ Tracked in: reports/report_inventory_log.html
├─ Foreign Keys:
│  ├─ product_id → Product
│  ├─ from_location_id → Location
│  ├─ to_location_id → Location
│  └─ stock_opname_id → StockOpname (if from opname)

STOCK_OPNAME
├─ Started in: inventory/stock_opname_locations.html
├─ Counted in: inventory/stock_opname_form.html
├─ Submitted for approval: inventory/stock_opname_approvals.html
├─ Detailed approval: inventory/stock_opname_approval_detail.html
├─ Historical view: master_data/stock_opname_session_detail.html
└─ Foreign Keys:
   ├─ location_id → Location
   └─ submitted_by → User

PURCHASE_ORDER
├─ Created in: inventory/stock_purchasing.html
├─ Tracked in: reports/purchasing_report.html
├─ Foreign Keys:
   ├─ vendor_id → Vendor
   ├─ location_id → Location
   └─ created_by → User

VENDOR
├─ Created/edited in: master_data/vendor_form.html
├─ Listed in: master_data/vendors_list.html
├─ Pricing: inventory/supplier_price_list.html
├─ Used in: inventory/stock_purchasing.html (purchase orders)
└─ Performance: reports/purchasing_report.html

CAMPAIGN
├─ Created in: marketing/add_campaign.html
├─ Listed in: marketing/campaign.html
├─ Performance: marketing/campaign_list.html
└─ Target audience: master_data/customers.html

DISCOUNT
├─ Managed in: marketing/discount.html
├─ Applied in: sales_insight/pos.html (during transaction)
└─ Impact tracked: reports/report_sales_by_outlet.html

LOCATION
├─ Created in: master_data/locations.html
├─ Used in: inventory/stock_opname_locations.html
├─ Stock levels: inventory/stock_overview.html
├─ Sales by location: reports/report_sales_by_outlet.html
└─ Used across: Most inventory & sales features

CATEGORY
├─ Created in: master_data/categories_list.html
├─ Referenced in: inventory/products.html
├─ Hierarchy: master_data/categories_list.html
└─ Reports: reports/report_sales_by_product.html
```

---

## 👥 User Role Access Matrix

### Role Definitions
```
┌─────────────┬──────────────┬─────────────┬──────────┬─────────┐
│ Module      │ Admin        │ Manager     │ Staff    │ Viewer  │
├─────────────┼──────────────┼─────────────┼──────────┼─────────┤
│ AUTH        │ Full (CRUD)  │ View        │ View     │ Own     │
│ SALES       │ Full (CRUD)  │ Full (CRUD) │ POS only │ View    │
│ INVENTORY   │ Full (CRUD)  │ Full (CRUD) │ Limited  │ View    │
│ MARKETING   │ Full (CRUD)  │ Full (CRUD) │ -        │ View    │
│ MASTER DATA │ Full (CRUD)  │ View/Edit   │ View     │ View    │
│ PRODUCTION  │ Full (CRUD)  │ View/Edit   │ View     │ View    │
│ REPORTS     │ Full Export  │ Full Export │ Limited  │ View    │
│ SETTINGS    │ Full (CRUD)  │ Limited     │ -        │ -       │
│ MESSAGES    │ Full         │ Full        │ Full     │ Limited │
└─────────────┴──────────────┴─────────────┴──────────┴─────────┘

Legend:
- Full (CRUD) = Create, read, update, delete everything
- Full Export = Can create, read, update, delete AND export
- View/Edit = Can read and edit but not create/delete
- View = Read-only access
- Limited = Restricted view (e.g., own data only)
- POS only = Access to POS interface only
- Own = Access to own profile only
- "-" = No access
```

### Feature Access by Role

**Admin:**
- Access to all modules
- Can create/delete users & assign roles
- System settings & backup
- All reports & exports
- Activity log view

**Manager:**
- All sales & inventory operations
- Can approve stock opnames & requisitions
- Reports with limited data (own location/team)
- Limited user management
- Cannot delete core data

**Staff:**
- POS transactions
- Limited inventory (view stock, create movements)
- View campaigns but cannot create
- Create customer records
- View assigned reports only

**Viewer:**
- Read-only access
- Can view reports
- Cannot create/modify anything
- View activity log (limited)

---

## 🔄 Process Workflows

### Workflow 1: Daily Sales Operations
```
Morning:
1. Staff login (auth/login.html)
2. Cashier: Dashboard (sales_insight/dashboard.html) - check KPIs
3. Manager: Check low stock (inventory/stock_overview.html)
   → If low: Create PO in inventory/stock_purchasing.html

Throughout Day:
4. Cashier: Process POS transactions (sales_insight/pos.html)
   → Customer lookup: master_data/customers.html
   → Apply discount: marketing/discount.html
   → Process payment: Select method in POS

End of Day:
5. Manager: Review daily summary (reports/transaction_summary.html)
6. Accountant: Export sales data (reports/sales_report.html)
7. Next day: Check requisition approvals (inventory/stock_opname_approvals.html)
```

### Workflow 2: Stock Opname (Physical Count)
```
Planning:
1. Manager schedules stock opname
2. Selects location (inventory/stock_opname_locations.html)

Execution:
3. Staff counts items (inventory/stock_opname_form.html)
   → Products listed with current system qty
   → Enter physical count qty
   → Note discrepancies
   → Submit

Review:
4. Manager reviews (inventory/stock_opname_approvals.html)
   → Click to view full detail (inventory/stock_opname_approval_detail.html)
   → Check variance %
   → Approve or reject

Finalize:
5. Approval creates stock movements (inventory/stock_movement.html)
   → Updates inventory levels
   → Visible in stock overview (inventory/stock_overview.html)
   → Historical record: master_data/stock_opname_session_detail.html
```

### Workflow 3: Purchase Order Process
```
Creation:
1. Manager views low stock (reports/report_inventory_low.html)
2. Creates PO (inventory/stock_purchasing.html)
   → Select vendor (master_data/vendors_list.html)
   → Select products (inventory/products.html)
   → Set quantities & expected delivery

Approval (if needed):
3. Submit for approval
4. Manager approves (via approval_modal.html)

Tracking:
5. View PO status (inventory/stock_purchasing.html)
6. Monitor in report (reports/purchasing_report.html)

Receipt:
7. Goods arrive
8. Create stock movement (inventory/add_stock_movement.html)
   → Movement type: "Receive PO"
   → Link to PO
   → Confirm quantities
9. Submit → Stock levels updated automatically
10. Historical tracking: reports/report_inventory_log.html
```

### Workflow 4: Customer Loyalty
```
Customer Creation:
1. Cashier creates customer during POS (sales_insight/pos.html)
   → Or created in (master_data/customer_form.html)

Loyalty Points:
2. Each transaction adds points
   → Based on spend amount
   → Stored in customer profile

View Profile:
3. Manager views customer (master_data/customer_detail.html)
   → See loyalty points balance
   → Redemption history

Redemption:
4. At POS (sales_insight/pos.html)
   → Cashier selects "Redeem Points"
   → Deducts from customer points balance

Loyalty Program:
5. Manager creates loyalty tiers (settings for programs)
6. Manage members (marketing/loyalty_members.html)
```

### Workflow 5: Campaign & Discount
```
Campaign Planning:
1. Manager creates campaign (marketing/add_campaign.html)
   → Campaign name & dates
   → Target audience: master_data/customers.html
   → Budget allocation

Discount Creation:
2. Creates discount (marketing/discount.html)
   → Discount amount or %
   → Eligible customers or products
   → Start/end date

Execution:
3. Discount automatically available at POS (sales_insight/pos.html)
4. Cashier applies when applicable

Performance:
5. Manager views campaign performance (marketing/campaign.html)
6. Analyze discount impact (reports/report_sales_by_outlet.html)
```

---

## 🛠️ Implementation Guide

### For Developers: Adding a New Feature

#### Step 1: Plan Data Model
```python
# In lumra_config/models.py
class NewFeature(models.Model):
    name = models.CharField(max_length=100)
    # ... other fields
```

#### Step 2: Create Views
```python
# In lumra_config/views/new_feature_views.py
def list_view(request):
    items = NewFeature.objects.all()
    return render(request, 'lumra_pages/new_module/list.html', 
                  {'items': items})

def form_view(request):
    # CRUD logic
    return render(request, 'lumra_pages/new_module/form.html', context)
```

#### Step 3: Create Templates
```html
<!-- lumra_pages/new_module/list.html -->
{% extends 'base/base.html' %}

{% block title %}
  New Feature - LUMRA
{% endblock %}

{% block content %}
  {% include 'base/navbar.html' %}
  {% include 'base/sidebar.html' %}
  
  <div class="main-content">
    <!-- List items -->
    {% for item in items %}
      <!-- Display item -->
    {% endfor %}
  </div>
{% endblock %}
```

#### Step 4: Create URLs
```python
# In lumra_config/urls/new_module_urls.py
urlpatterns = [
    path('', list_view, name='list'),
    path('create/', form_view, name='create'),
    # ...
]
```

#### Step 5: Add to Sidebar
```html
<!-- In base/sidebar.html -->
<a href="{% url 'new_module:list' %}" class="menu-item">
  <i class="icon"></i>
  New Feature
</a>
```

#### Step 6: Link to Other Modules
```html
<!-- In other module templates -->
<a href="{% url 'new_module:list' %}">View New Feature</a>
```

---

### Connecting an Existing Module to Another

#### Example: Connect Product to Recipe

**Before:** Recipe → Manually enter ingredients  
**After:** Recipe → Link to actual products

**Steps:**
1. Modify Recipe model to include Product FK
2. Update recipe_form.html to show product selector
3. Update recipe_detail.html to display products
4. Add link from inventory/products.html to recipes
5. Update reports to calculate recipe costing

---

## 📊 System Statistics

| Metric | Count |
|--------|-------|
| Total Templates | 102 |
| Business Modules | 10 |
| Base Components | 14 |
| Data Models | 50+ |
| Views (Functions) | 100+ |
| URL Routes | 150+ |
| User Roles | 4 |
| Report Types | 15 |
| Workflow Steps | 5 major |
| Authentication Methods | Username/Password + 2FA |
| Export Formats | PDF, Excel, CSV |

---

## 🎯 Quick Reference Card

```
MOST COMMON WORKFLOWS:

Sales Day:      auth/login → dashboard → pos → transaction_summary
Inventory Mgmt: products → stock_overview → low_stock → purchasing
Stock Count:    opname_locations → opname_form → approvals → movements
Reports:        dashboard → reporting hub → specific_report → export
Admin:          users → settings → business_settings → monitor
```

---

**This document provides the complete system overview. Reference it when planning feature additions or understanding how modules interact.**
