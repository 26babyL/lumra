# 🏗️ LUMRA ERP - Component Architecture & Connections
**How Templates Connect, Inherit, and Reference Each Other**  
*Generated: April 10, 2026*

---

## 📑 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Template Inheritance Hierarchy](#template-inheritance-hierarchy)
3. [Shared Components & Partials](#shared-components--partials)
4. [Navigation & Flow](#navigation--flow)
5. [Data Flow Between Templates](#data-flow-between-templates)
6. [Module Organization](#module-organization)
7. [Integration Points](#integration-points)

---

## 🏗️ Architecture Overview

### Project Structure
```
lumra_config/
├── templates/
│   ├── base/                          [Shared layout & components]
│   │   ├── base.html                  ← ROOT template
│   │   ├── navbar.html                ← Top navigation bar
│   │   ├── sidebar.html               ← Left navigation
│   │   ├── sidebar_item.html          ← Menu item component
│   │   ├── sidebar_right.html         ← Additional panels
│   │   ├── footer.html                ← Page footer
│   │   ├── alert*.html                ← Alert/notification components
│   │   ├── approval_modal.html        ← Approval workflow modal
│   │   ├── kpi_card*.html             ← Dashboard KPI cards
│   │   └── partials/                  ← Reusable snippets
│   │       ├── form_field.html        ← Form input component
│   │       └── bg_blob.html           ← SVG decoration
│   │
│   └── lumra_pages/                   [Feature-specific pages]
│       ├── auth/                      [2 templates: login, register]
│       ├── inventory/                 [16 templates: products, stock, purchasing]
│       ├── sales_insight/             [7 templates: POS, dashboard, reports]
│       ├── production/                [3 templates: recipes]
│       ├── marketing/                 [5 templates: campaigns, loyalty]
│       ├── master_data/               [13 templates: categories, units, etc]
│       ├── messages/                  [2 templates: inbox, notifications]
│       ├── reports/                   [20 templates: sales, inventory, financial]
│       ├── settings/                  [10 templates: users, configuration]
│       └── etc/                       [3 templates: error pages]
```

### Template Naming Convention
```
lumra_pages/{module}/{feature}.html

Examples:
- lumra_pages/inventory/products.html
- lumra_pages/sales_insight/pos.html
- lumra_pages/master_data/customers_list.html
- lumra_pages/reports/sales_report.html
- lumra_pages/settings/business_settings.html
```

### File Count Summary
- **Base Components:** 14 files
- **Authentication:** 2 files
- **10 Business Modules:** 86 files (inventory, sales, marketing, etc.)
- **Total:** 102 template files

---

## 📐 Template Inheritance Hierarchy

### Level 1: Root Template
```
base.html
├── DOCTYPE & <head>
├── CSS/JS imports (Tailwind, Alpine.js, Font Awesome)
├── {% block title %}
├── {% block extra_head %}
├── {% block extra_css %}
├── {% block chart_scripts %}
├── <body> with sidebar/navbar divs
└── {% block content %}  ← ALL other templates inject here
```

**Location:** `lumra_config/templates/base/base.html`

### Level 2: Page Templates
All feature pages inherit from base.html:

```
{% extends 'base/base.html' %}

{% block title %}
  Page Title
{% endblock %}

{% block content %}
  <div class="container">
    <!-- Page-specific HTML -->
  </div>
{% endblock %}

{% block extra_css %}
  <!-- Page-specific CSS if needed -->
{% endblock %}

{% block chart_scripts %}
  <!-- Chart libraries for this page -->
{% endblock %}
```

### Example: Inventory Products Page
```
FILE: lumra_pages/inventory/products.html

{% extends 'base/base.html' %}

{% block title %}
  Products - Inventory Management
{% endblock %}

{% block content %}
  {% include 'base/navbar.html' %}
  {% include 'base/sidebar.html' %}
  
  <div class="main-content">
    <!-- Products list table -->
    <!-- Uses form_field.html for filters -->
  </div>
  
  <!-- May include approval_modal.html for bulk actions -->
  <!-- May include alert.html for notifications -->
{% endblock %}
```

---

## 🧩 Shared Components & Partials

### 1. Navigation Components

#### navbar.html
**Purpose:** Top navigation bar  
**Used By:** All authenticated pages  
**Contains:**
- Search bar (Alpine.js reactive)
- User profile dropdown
- Notification bell icon
- Language/theme selector
- Quick action buttons

**Included in:** base.html (main layout)

**Alpine.js Features:**
- Search overlay toggle
- User menu dropdown
- Notification badge count

---

#### sidebar.html
**Purpose:** Left navigation menu  
**Used By:** All authenticated pages  
**Contains:**
- Module menu items
- Repeated `sidebar_item.html` for each menu
- Collapsible submenu groups
- Active item highlighting
- Mobile toggle button

**Included in:** base.html (main layout)

**Dynamic Elements:**
- Menu items from Django context (module permissions)
- Active state based on current URL
- Collapsible sections (Alpine.js)

---

#### sidebar_item.html
**Purpose:** Individual menu item component  
**Used By:** sidebar.html (repeated for each menu item)  
**Contains:**
- Icon + label
- Active state CSS
- Link href
- Optional submenu indicator

**Example Usage in sidebar.html:**
```html
{% for item in menu_items %}
  {% include 'base/sidebar_item.html' with 
    label=item.label 
    url=item.url 
    icon=item.icon 
    active=item.is_active
  %}
{% endfor %}
```

---

### 2. Alert & Modal Components

#### alert.html
**Purpose:** Full-page alert container  
**Used By:** Error pages (403, 404, 500)  
**Contains:**
- Alert wrapper with styling
- Alert type styling (error, warning, info, success)
- Includes `alert_inner.html`

**Example (error_404.html):**
```html
{% extends 'base/base.html' %}
{% include 'base/alert.html' with alert_type='error' %}
```

---

#### alert_inner.html
**Purpose:** Alert message content component  
**Used By:** 
- alert.html (error pages)
- Modal windows (verification before actions)
- In-page notifications

**Contains:**
- Icon + message
- Action buttons (Close, Go Back, Retry)
- Optional additional details

---

#### approval_modal.html
**Purpose:** Modal for approval workflows  
**Used By:** 
- Stock opname approval workflow
- Purchase order approval
- Requisition approval
- Any confirmation workflow

**Contains:**
- Modal header with title
- Item details to approve
- Approve/Reject buttons with notes
- Modal backdrop & close button

**Alpine.js Integration:**
```html
<div x-show="approvalModal" @click.outside="approvalModal = false">
  <!-- Modal content -->
  <button @click="approveItem()">Approve</button>
  <button @click="rejectItem()">Reject</button>
</div>
```

---

### 3. Form Components

#### partials/form_field.html
**Purpose:** Reusable form input component  
**Used By:** All form pages (25+ templates with forms)  
**Parameters:**
- `field_type`: 'text', 'email', 'number', 'select', 'textarea', 'date'
- `label`: Field label text
- `name`: HTML name attribute
- `value`: Pre-filled value (edit mode)
- `required`: Boolean
- `options`: For select fields
- `placeholder`: Placeholder text
- `error`: Error message if validation failed

**Example (customer_form.html):**
```html
{% include 'base/partials/form_field.html' with
  field_type='text'
  label='Customer Name'
  name='customer_name'
  required=True
%}

{% include 'base/partials/form_field.html' with
  field_type='select'
  label='Customer Type'
  name='customer_type'
  options=customer_types
%}

{% include 'base/partials/form_field.html' with
  field_type='textarea'
  label='Address'
  name='address'
  placeholder='Enter customer address'
%}
```

**Features:**
- Consistent styling across all forms
- Built-in validation styling
- Accessibility attributes (labels, aria-*)
- Tailwind CSS responsive classes

---

#### partials/bg_blob.html
**Purpose:** Decorative background element  
**Used By:** 
- auth/login.html
- auth/register.html
- Error pages (optional)

**Contains:** SVG blob shape for visual interest

---

### 4. Dashboard Components

#### kpi_card.html
**Purpose:** Dark-themed KPI display card  
**Used By:** dashboard.html, financial_reports.html  
**Contains:**
- KPI title
- Large number display
- Trend indicator (↑↓)
- Percentage change
- Icon
- Optional chart sparkline

**Tailwind Classes:** Dark background, emerald accent

---

#### kpi_card_inner.html
**Purpose:** KPI card content wrapper  
**Used By:** kpi_card.html (inner structure)  
**Contains:**
- Metric label
- Metric value
- Trend colors (green for up, red for down)

---

#### kpi_card_white.html
**Purpose:** White-themed KPI display card  
**Used By:** dashboard.html (alternative styling)  
**Contains:** Same content as `kpi_card.html` but with light theme

---

### 5. Footer Component

#### footer.html
**Purpose:** Page footer  
**Used By:** 
- auth/login.html
- auth/register.html
- Error pages

**Contains:**
- Copyright notice
- Links (Privacy, Terms, Support)
- Year auto-update

---

## 🔄 Navigation & Flow

### User Navigation Paths

#### Path 1: Dashboard → Inventory
```
1. User logs in (auth/login.html)
2. Redirected to (sales_insight/dashboard.html)
3. Dashboard shows KPI cards using (kpi_card.html)
4. User clicks "Inventory" in sidebar.html
5. Default: goes to (inventory/products.html)
6. From there can access:
   - stock_overview.html
   - stock_movement.html
   - stock_planning.html
   - supplier_price_list.html
```

#### Path 2: Dashboard → Reports
```
1. Dashboard (sales_insight/dashboard.html)
2. Click "Reports" menu
3. Redirect to (reports/reporting.html) - report hub
4. Select specific report:
   - sales_report.html
   - report_sales_by_product.html
   - report_profit_loss_detail.html
   - etc.
```

#### Path 3: Master Data Management
```
1. Settings menu → Master Data
2. Can access any of:
   - categories_list.html
   - units_list.html
   - vendors_list.html
   - customers_list.html
   - locations.html
```

### URL Linking Pattern
```
<a href="{% url 'app_name:view_name' %}">
  Link Text
</a>

Examples:
<a href="{% url 'inventory:products' %}">Products</a>
<a href="{% url 'sales:pos' %}">POS</a>
<a href="{% url 'master_data:customers' %}">Customers</a>
<a href="{% url 'reports:sales_report' %}">Sales Report</a>
```

---

## 📊 Data Flow Between Templates

### Example 1: Creating a Product
```
Flow:
1. View products list (inventory/products.html)
2. Click "Add Product" button
3. Opens form (inventory/product_form.html)
4. Form uses partials/form_field.html for:
   - Product name (text)
   - Category (dropdown from master_data)
   - Unit (dropdown from master_data)
   - Price (number)
5. User submits form
6. Django view saves product
7. Redirect back to (inventory/products.html)
8. New product appears in list

Dependencies:
- master_data/categories_list.html (provides categories dropdown)
- master_data/units_list.html (provides units dropdown)
```

### Example 2: Stock Movement
```
Flow:
1. From dashboard (sales_insight/dashboard.html)
2. Click low stock alert
3. Go to (inventory/stock_overview.html)
4. Identify low item
5. Click "Create Movement"
6. Form (inventory/add_stock_movement.html)
   - Movement type: Transfer/Adjustment/Damage
   - From location: dropdown from master_data/locations.html
   - Product: search/select
   - Quantity: number
7. Submit
8. Django creates stock movement record
9. Redirect to (inventory/stock_movement.html)
10. See new movement in log

Dependencies:
- master_data/locations.html (location data)
- inventory/products.html (product data)
- inventory/add_stock_movement.html (form)
```

### Example 3: POS Transaction
```
Flow:
1. Cashier navigates to (sales_insight/pos.html)
2. Template loads:
   - Product list (from inventory)
   - Customer dropdown (from master_data)
   - Payment methods (from settings)
3. Cashier selects items → Added to cart
4. Cart totals calculated (real-time, Alpine.js)
5. Select customer from (master_data/customers_list.html)
6. Apply discount from marketing_discount.html data
7. Select payment method
8. Process transaction
9. Django saves transaction
10. Receipt printed
11. Redirect back to POS for next transaction
12. Transaction appears in:
    - reports/sales_history.html
    - reports/transaction_summary.html
    - sales_insight/dashboard.html (KPI update)

Dependencies:
- inventory/products.html (product catalog)
- master_data/customers_list.html (customer data)
- marketing/discount.html (discount rules)
```

### Example 4: Stock Opname Workflow
```
Flow:
1. Manager navigates to Stock Opname
2. (inventory/stock_opname_locations.html) - Select location
3. Click location → Open (inventory/stock_opname_form.html)
4. Display all products with current qty
5. Staff enters physical counted quantities
6. Submit form
7. Django validates submission
8. Manager sees in (inventory/stock_opname_approvals.html)
9. Click approval → (inventory/stock_opname_approval_detail.html)
10. Review discrepancies
11. Click "Approve" → Opens approval_modal.html
12. Confirm approval → Django creates journal entries
13. Stock updated in (inventory/stock_movement.html)
14. Historical record in (master_data/stock_opname_session_detail.html)

Dependencies:
- master_data/locations.html (location reference)
- inventory/products.html (product reference)
- base/approval_modal.html (approve/reject action)
```

---

## 🏢 Module Organization

### Module Layout Pattern

Each business module follows this structure:

```
lumra_pages/{module}/
├── List/Dashboard views        (e.g., products.html, campaign.html)
├── Detail views                (e.g., product_details.html)
├── Form views (CRUD)           (e.g., customer_form.html)
├── Report views                (e.g., sales_report.html)
└── Supporting views            (e.g., approval modals)

Connected by:
- base/sidebar.html (menu item)
- base/navbar.html (search results)
- Cross-linking via URLs
```

### Module Connections

#### Inventory Module Dependencies
```
inventory/
├── products.html              → Links to master_data (categories, units)
├── product_details.html       → Shows stock from locations
├── stock_movement.html        → Links to add_stock_movement.html
├── stock_planning.html        → Links to stock_purchasing.html
├── stock_purchasing.html      → Links to master_data/vendors
├── supplier_price_list.html   → Tracks vendor pricing
├── stock_opname_*.html        → Workflow files (locations → form → approval)
└── add_stock_movement.html    → Connects to master_data (locations, products)

Connections to Other Modules:
- → reports/report_inventory_*.html (reports)
- → reports/requisition_report.html (requisitions)
- → reports/purchasing_report.html (purchasing)
- → sales_insight/dashboard.html (stock alerts)
- → master_data/* (categories, units, vendors, locations)
```

#### Sales Module Dependencies
```
sales_insight/
├── pos.html                   → Links to inventory (products)
├── dashboard.html             → Shows data from POS + inventory + customers
├── sales_intelligence.html    → Analysis of POS transactions
├── sales_performance.html     → Performance metrics
├── financial_reports.html     → Financial summary
├── market_insights.html       → Market analysis
└── trends_analysis.html       → Historical trends

Connections to Other Modules:
- → master_data/customers.html (customer lookup)
- → master_data/locations.html (location selection)
- → master_data (categories for product filtering)
- → marketing (discounts applied at POS)
- → reports/sales_report.html (detailed sales)
- → reports/report_sales_by_*.html (breakdowns)
```

#### Reports Module Connections
```
reports/
├── reporting.html             → Hub linking to all reports
├── sales_report.html          → From sales_insight/pos.html
├── report_inventory_*.html    → From inventory/* data
├── report_profit_loss_detail.html → From sales + costs
├── requisition_report.html    → From inventory requisitions
├── purchasing_report.html     → From purchase orders
├── activity_log.html          → From all transaction logs
└── transaction_summary.html   → From POS transactions

Data Sources:
- All reports pull from Django database
- View calculations done in views.py
- Templates just display pre-calculated data
```

---

## 🔗 Integration Points

### 1. Navbar Integration

**navbar.html** includes:
```html
<!-- Search -->
<input type="search" 
       x-model="searchQuery" 
       @input="performSearch()">

<!-- User Dropdown -->
<div x-show="userDropdown">
  <a href="{% url 'settings:profile' %}">Profile</a>
  <a href="{% url 'auth:logout' %}">Logout</a>
</div>

<!-- Notification Bell -->
<span class="notification-badge" 
      x-text="notificationCount">
  0
</span>
```

### 2. Sidebar Integration

**sidebar.html** includes:
```html
<a href="{% url 'sales:dashboard' %}" 
   class="menu-item {% if current_app == 'sales' %}active{% endif %}">
  Dashboard
</a>

<a href="{% url 'inventory:products' %}" 
   class="menu-item {% if current_app == 'inventory' %}active{% endif %}">
  Inventory
</a>

{% for module in user_accessible_modules %}
  {% include 'base/sidebar_item.html' with 
    label=module.name 
    url=module.url
  %}
{% endfor %}
```

### 3. Alert Integration

**Page shows alert.html:**
```html
{% if messages %}
  {% include 'base/alert.html' with
    alert_type='error'
    message=messages.0
  %}
{% endif %}
```

### 4. Modal Integration

**Approval workflow uses approval_modal.html:**
```html
<!-- In inventory/stock_opname_approval_detail.html -->
<button @click="approvalModal = true">
  Approve Opname
</button>

{% include 'base/approval_modal.html' %}
```

### 5. Form Integration

**All forms use form_field.html:**
```html
<!-- In customer_form.html -->
{% include 'base/partials/form_field.html' with
  field_type='text'
  label='Name'
  name='name'
  value=customer.name
  required=True
%}
```

### 6. KPI Integration

**Dashboard uses KPI cards:**
```html
<!-- In sales_insight/dashboard.html -->
{% include 'base/kpi_card.html' with
  kpi_title='Today Sales'
  kpi_value=total_sales
  kpi_trend=percent_change
%}

{% include 'base/kpi_card_white.html' with
  kpi_title='Transactions'
  kpi_value=transaction_count
  kpi_trend=transaction_trend
%}
```

---

## 🔌 Front-end Technology Stack

### Alpine.js Integration Points

**Navbar search (navbar.html):**
```html
<div x-data="{ searchActive: false, searchQuery: '' }">
  <input @focus="searchActive = true" 
         @blur="searchActive = false"
         x-model="searchQuery">
</div>
```

**Sidebar toggle (sidebar.html):**
```html
<div x-data="{ sidebarOpen: true }">
  <nav :class="sidebarOpen ? 'w-64' : 'w-20'">
    ...
  </nav>
  <button @click="sidebarOpen = !sidebarOpen">
    Toggle
  </button>
</div>
```

**Modal workflows (approval_modal.html):**
```html
<div x-show="approvalModal" x-cloak>
  <form @submit.prevent="submitApproval()">
    <button @click="approveAction()">Approve</button>
  </form>
</div>
```

### CSS Framework Integration

**Tailwind CSS utility classes:**
- Responsive: `lg:w-64 md:w-40 sm:w-32`
- Spacing: `p-4 m-2 space-y-4`
- Colors: `bg-emerald-600 text-slate-800 border-amber-300`
- Flexbox: `flex justify-between items-center`

**CSS Modules/Custom Styles:**
- Dark/light theme variables (CSS custom properties)
- Glassmorphism effects (backdrop blur)
- Animations via Tailwind

---

## 🎯 Best Practices for Connecting Templates

1. **Always extend base.html** for consistency
   ```html
   {% extends 'base/base.html' %}
   ```

2. **Use named URL patterns** for linking
   ```html
   <a href="{% url 'inventory:products' %}">Products</a>
   ```

3. **Reuse form_field.html** for all forms
   ```html
   {% include 'base/partials/form_field.html' ... %}
   ```

4. **Include navbar & sidebar** in main content block
   ```html
   {% include 'base/navbar.html' %}
   {% include 'base/sidebar.html' %}
   ```

5. **Use approval_modal.html** for workflows
   ```html
   {% include 'base/approval_modal.html' %}
   ```

6. **Data from context** passed via Django view
   ```python
   # In views.py
   context = {
       'products': Product.objects.all(),
       'categories': Category.objects.all(),
   }
   return render(request, 'inventory/products.html', context)
   ```

7. **Alpine.js for interactivity** not server round-trips
   ```html
   <button @click="deleteItem(item.id)" @confirm>Delete</button>
   ```

---

**Reference this document when building new pages or modifying connections between templates.**
