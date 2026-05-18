# 🔗 LUMRA ERP - Feature to File Mapping
**Which Files Support Which Business Features**  
*Generated: April 10, 2026*

---

## 📑 Quick Index
- [Sales & Transactions](#sales--transactions)
- [Inventory Management](#inventory-management)
- [Product Management](#product-management)
- [Stock Opname (Physical Count)](#stock-opname-physical-count)
- [Purchasing & Suppliers](#purchasing--suppliers)
- [Master Data](#master-data)
- [Marketing & Loyalty](#marketing--loyalty)
- [Production/Recipes](#productionrecipes)
- [Reports & Analytics](#reports--analytics)
- [User Management & Access](#user-management--access)
- [System & Administration](#system--administration)
- [Customer Management](#customer-management)

---

## 💰 Sales & Transactions

### Point of Sale (POS)
**Feature Purpose:** Real-time sales transactions at checkout  
**Related Templates:**
- `sales_insight/pos.html` - POS interface with shopping cart
- `sales_insight/dashboard.html` - Daily sales summary (shows POS performance)
- `master_data/customers.html` - Customer lookup during POS
- `sales_insight/sales_intelligence.html` - Sales analytics post-transaction

**Data Flow:** Customer → Items → Cart → Payment → pos.html processes → Dashboard shows results

**Connections:**
- POS creates transactions → viewed in `sales_report.html`
- Customer history → tracked in `sales_history.html`
- Payment methods → breakdown in `report_sales_by_payment.html`

---

### Daily Sales Tracking
**Feature Purpose:** Monitor sales throughout the day  
**Related Templates:**
- `sales_insight/dashboard.html` - Today's total sales, transaction count, top products
- `sales_insight/sales_performance.html` - Sales metrics & trends
- `reports/sales_report.html` - Detailed sales analysis
- `reports/transaction_summary.html` - Daily transaction overview

**KPI Display:** Uses `base/kpi_card.html` and `base/kpi_card_white.html`

**Typical Workflow:** Manager opens Dashboard → Views KPIs → Clicks "Detailed Report" → `sales_report.html`

---

### Sales History
**Feature Purpose:** Query past transactions  
**Related Templates:**
- `reports/sales_history.html` - All transactions (chronological)
- `reports/sales_history_product.html` - Sales by product
- `sales_insight/sales_performance.html` - Performance analysis
- `reports/transaction_summary.html` - Summary view

**Filters:** Date range, customer, payment method, location

---

### Sales by Location
**Feature Purpose:** Compare performance across outlets  
**Related Templates:**
- `reports/report_sales_by_outlet.html` - Sales per location
- `master_data/locations.html` - Location master data
- `sales_insight/sales_intelligence.html` - Market insights

**Used By:** Regional managers, executives

---

### Payment Processing
**Feature Purpose:** Record different payment types  
**Related Templates:**
- `sales_insight/pos.html` - Payment selector during POS
- `reports/report_sales_by_payment.html` - Payment breakdown analysis
- `reports/transaction_summary.html` - Payment summaries

**Payment Types Tracked:** Cash, Card, Mobile money, etc.

---

## 📦 Inventory Management

### Product Listing & Search
**Feature Purpose:** View & manage all products  
**Related Templates:**
- `inventory/products.html` - Main product dashboard
- `inventory/product_list.html` - Paginated product list
- `inventory/product_details.html` - Detailed product view
- `master_data/categories_list.html` - Product categories (linked)
- `settings/search.html` - Global search for products

**Stock Display:** Shows current stock per location using aggregation

**Navigation Path:** Dashboard → Inventory menu → `products.html` → Click product → `product_details.html`

---

### Stock Levels & Alerts
**Feature Purpose:** Monitor low stock situations  
**Related Templates:**
- `inventory/stock_overview.html` - Dashboard with low stock alerts
- `reports/report_inventory_low.html` - Low stock report
- `reports/report_inventory_stock.html` - Current stock levels
- `inventory/stock_movement.html` - Transaction history

**Alert Rules:** Products below minimum quantity flagged

**Actions from Alert:** 
1. Create purchase order in `inventory/stock_purchasing.html`
2. Create stock movement in `inventory/add_stock_movement.html`

---

### Stock by Location
**Feature Purpose:** Track inventory distributed across outlets  
**Related Templates:**
- `inventory/stock_overview.html` - Stock breakdown by location
- `master_data/locations.html` - Location master
- `inventory/stock_planning.html` - Allocation by location
- `reports/report_inventory_stock.html` - Stock level report

**Typical Use:** Rebalance stock → Use `inventory/stock_movement.html` to transfer

---

## 🏷️ Product Management

### Create/Edit Products
**Feature Purpose:** Add new products or modify existing ones  
**Related Templates:**
- `inventory/products.html` - Product list (edit action)
- `inventory/product_details.html` - View → Edit link
- Form uses component: `base/partials/form_field.html`
- Master data: `master_data/categories_list.html` (select category)

**Product Attributes:**
- Name, code, description
- Category (FK to categories)
- Unit of measure (FK to units)
- Price (cost, retail, wholesale)
- Reorder level (for low stock alerts)
- Status (active/inactive)

**Form Page Construction:**
```
page extends base.html
  ├── navbar.html
  ├── sidebar.html
  ├── form uses form_field.html (multiple times)
  │   ├── Product name (text)
  │   ├── Category (dropdown to categories_list data)
  │   ├── Unit (dropdown to units_list data)
  │   └── ... other fields ...
  └── Save/Cancel buttons
```

---

### Product Pricing
**Feature Purpose:** Define cost and selling prices  
**Related Templates:**
- `inventory/supplier_price_list.html` - Supplier pricing
- `inventory/supplier_price_form.html` - Add/edit supplier price
- Related to `inventory/stock_purchasing.html` (purchase orders)

**Price Types:**
- Cost price (from supplier)
- Retail price
- Wholesale price (if applicable)

**Connections:**
- Cost price → Used in P&L calculations (`reports/report_profit_loss_detail.html`)
- Retail price → Used in POS (`sales_insight/pos.html`)

---

### Supplier Price Management
**Feature Purpose:** Track pricing from different vendors  
**Related Templates:**
- `inventory/supplier_price_list.html` - All supplier prices
- `inventory/supplier_price_form.html` - Add/edit supplier price
- `inventory/supplier_price_confirm_delete.html` - Confirm deletion
- Connects to: `master_data/vendors_list.html` (vendor master)

**Price History:** MOQ (minimum order qty), effective dates for price changes

---

## 📊 Stock Opname (Physical Count)

### Create Stock Opname
**Feature Purpose:** Physical inventory count workflow  
**Related Templates:**
- `inventory/stock_opname_locations.html` - Select location to count
- `inventory/stock_opname_form.html` - Enter counted quantities
- `inventory/stock_opname_approvals.html` - Review submitted counts
- `inventory/stock_opname_approval_detail.html` - Approve/reject detail

**Workflow:**
```
1. Start: Click "New Stock Opname" in stock_opname_locations.html
2. Count: Enter actual quantities in stock_opname_form.html
3. Submit: Form submits for approval
4. Approve: Manager reviews in stock_opname_approvals.html
5. Approve Detail: Click opname → stock_opname_approval_detail.html
6. Finalize: Approval creates journal entry → Updates stock_movement.html
```

**Variance Tracking:** Shows current qty vs counted qty with discrepancy %

---

### Stock Opname History
**Feature Purpose:** View past physical counts and results  
**Related Templates:**
- `master_data/stock_opname_session_detail.html` - Historical session details
- `inventory/stock_opname_approvals.html` - Approved sessions archive
- `reports/activity_log.html` - Who counted, when, results

### Stock Opname Approvals
**Feature Purpose:** Review & approve submitted stock counts  
**Related Templates:**
- `inventory/stock_opname_approvals.html` - List of pending approvals
- `inventory/stock_opname_approval_detail.html` - Detail view with discrepancy analysis
- Modal: `base/approval_modal.html` (for approve/reject action)

**Trigger:** Used after `inventory/stock_opname_form.html` submission

---

## 🛒 Purchasing & Suppliers

### Purchase Orders
**Feature Purpose:** Create & track purchase orders to suppliers  
**Related Templates:**
- `inventory/stock_purchasing.html` - PO list & creation
- Linked to: `master_data/vendors_list.html` (select vendor)
- Linked to: `inventory/products.html` (select products)
- Linked to: `reports/purchasing_report.html` (PO analysis)

**PO Workflow:**
1. Create PO in `stock_purchasing.html` (select vendor, products, qty, expected date)
2. Submit for approval
3. Track delivery status
4. Receive goods → Create stock movement in `inventory/stock_movement.html`

---

### Supplier Management
**Feature Purpose:** Maintain vendor/supplier records  
**Related Templates:**
- `master_data/vendors_list.html` - Vendor list
- `master_data/vendor_list.html` - Alternative view
- `master_data/vendor_form.html` - Create/edit vendor info
- `inventory/supplier_price_list.html` - Pricing per supplier
- `reports/purchasing_report.html` - Vendor spending analysis

**Vendor Attributes:**
- Company name, contact person
- Phone, email, website
- Address, tax number
- Payment terms, status (active/inactive)

---

### Stock Requisitions
**Feature Purpose:** Inter-location stock request workflow  
**Related Templates:**
- `inventory/add_stock_movement.html` - Request stock transfer
- `reports/requisition_report.html` - Requisition history & tracking
- `inventory/stock_movement.html` - Shows fulfilled requisitions as movements

**Requisition Status:** Requested → Approved → Fulfilled → Received

---

## 🗂️ Master Data

### Categories
**Feature Purpose:** Organize products into logical groups  
**Related Templates:**
- `master_data/categories_list.html` - Category list
- `master_data/category_form.html` - Create/edit category
- Used in: `inventory/products.html` (category filter)
- Used in: `reports/report_sales_by_product.html` (category breakdown)

**Hierarchy:** Supports parent/child categories (e.g., Beverages > Hot Drinks)

---

### Units of Measurement
**Feature Purpose:** Define product measurement units  
**Related Templates:**
- `master_data/units_list.html` - Unit list (kg, liter, piece, etc.)
- `master_data/unit_form.html` - Create/edit unit
- Used in: `inventory/products.html` (unit selection)
- Used in: `inventory/add_stock_movement.html` (unit for movement)

---

### Locations/Outlets
**Feature Purpose:** Define store locations/warehouses  
**Related Templates:**
- `master_data/locations.html` - Location list
- `master_data/location_list.html` - Alternative view
- Used in: All stock-related features (location selection)
- Used in: `reports/report_sales_by_outlet.html` (sales per location)
- Modal reference: Location picker in forms

---

### Vendors/Suppliers
**Feature Purpose:** Maintain supplier list  
**Related Templates:**
- `master_data/vendors_list.html` - Vendor list
- `master_data/vendor_list.html` - Alternative view
- `master_data/vendor_form.html` - Create/edit vendor
- Used in: `inventory/stock_purchasing.html` (select vendor for PO)
- Used in: `inventory/supplier_price_list.html` (supplier prices)

---

## 👥 Customer Management

### Customers List
**Feature Purpose:** Maintain customer database  
**Related Templates:**
- `master_data/customers.html` - Customer dashboard
- `master_data/customers_list.html` - Customer list (paginated)
- `master_data/customer_detail.html` - Customer profile
- `master_data/customer_form.html` - Create/edit customer
- `master_data/customer.html` - Alternative customer view

**Customer Data:**
- Name, email, phone, address
- Customer type (retail/wholesale)
- Birth date (for promotions)
- Purchase history summary
- Loyalty points balance

---

### Customer Lookup in POS
**Feature Purpose:** Find customer during checkout  
**Related Templates:**
- `sales_insight/pos.html` - Search customer during POS
- Links to: `master_data/customers_list.html` (create new customer quick link)
- Result: Transaction linked to customer → Visible in `master_data/customer_detail.html`

**Data Used:**
- Customer name for receipt
- Discount eligibility
- Loyalty points

---

### Customer Loyalty
**Feature Purpose:** Track & manage loyalty program  
**Related Templates:**
- `marketing/loyalty_members.html` - Member list with points
- `master_data/customer_detail.html` - Shows points balance
- Used in: `sales_insight/pos.html` (points deduction during redemption)
- Report: `reports/loyalty_members.html` (if exists)

---

## 📢 Marketing & Loyalty

### Campaign Management
**Feature Purpose:** Plan & execute marketing campaigns  
**Related Templates:**
- `marketing/campaign.html` - Campaign list
- `marketing/campaign_list.html` - Alternative view
- `marketing/add_campaign.html` - Create campaign
- Connects to: `master_data/customers.html` (target audience)

**Campaign Fields:**
- Name, description
- Start/end date
- Budget, target audience
- Campaign type (promotion, seasonal, etc.)
- Performance tracking

---

### Discount Management
**Feature Purpose:** Create promotional discounts  
**Related Templates:**
- `marketing/discount.html` - Discount list
- Used in: `sales_insight/pos.html` (apply discount at checkout)
- Tracked in: `reports/report_sales_by_outlet.html` (discount impact)

**Discount Type:**
- Amount-based (e.g., $2 off)
- Percentage-based (e.g., 10% off)
- Eligibility rules (customer type, purchase amount, etc.)

---

### Loyalty Program
**Feature Purpose:** Reward repeat customers  
**Related Templates:**
- `marketing/loyalty_members.html` - Member list
- `master_data/customer_detail.html` - Member profile with points
- Used in: `sales_insight/pos.html` (accrue/redeem points)
- Links to: `master_data/customers.html` (member enrollment)

---

## 🏭 Production/Recipes

### Recipe Management
**Feature Purpose:** Define recipes for manufactured products  
**Related Templates:**
- `production/recipe_list.html` - Recipe catalog
- `production/recipe_form.html` - Create/edit recipe
- `production/recipe_detail.html` - View recipe details
- Used in: Costing & COGS calculation (`reports/report_profit_loss_detail.html`)

**Recipe Components:**
- Ingredients (products)
- Quantities per ingredient
- Yield amount
- Total cost (auto-calculated)

**Uses:**
- Determine product cost
- Generate material requirements
- Track ingredient usage

---

## 📊 Reports & Analytics

### Sales Reports
**Feature Purpose:** Analyze sales performance  
**Related Templates:**
- `reports/sales_report.html` - Main sales report (period, products, etc.)
- `reports/sales_history.html` - All transactions chronologically
- `reports/sales_history_product.html` - Sales by product
- `reports/report_sales_by_outlet.html` - Sales per location
- `reports/report_sales_by_payment.html` - Payment method breakdown
- `reports/report_sales_by_product.html` - Product performance ranking

**Data Source:** POS transactions via `sales_insight/pos.html`

**Typical Report User:** Sales manager, accountant

---

### Inventory Reports
**Feature Purpose:** Analyze stock & supply chain  
**Related Templates:**
- `reports/report_inventory_stock.html` - Current stock levels
- `reports/report_inventory_log.html` - Stock transaction history
- `reports/report_inventory_low.html` - Low stock alert
- `inventory/stock_overview.html` - Dashboard view

**Data Source:** Stock movements, opname submissions

---

### Financial Reports
**Feature Purpose:** Executive financial overview  
**Related Templates:**
- `sales_insight/financial_reports.html` - Revenue, expense, profit summary
- `reports/report_profit_loss_detail.html` - Detailed P&L by category/period
- Includes: Revenue, COGS, operating expenses, profit/loss

**Data Sources:**
- Sales from POS
- Cost from suppliers & recipes
- Expenses from settings

---

### Operational Reports
**Feature Purpose:** Track internal processes  
**Related Templates:**
- `reports/requisition_report.html` - Stock requisition status
- `reports/purchasing_report.html` - Purchase order tracking
- `reports/transfer_report.html` - Inter-location stock transfers
- `reports/activity_log.html` - User activity audit trail

---

### Dashboard & KPIs
**Feature Purpose:** Executive summary view  
**Related Templates:**
- `sales_insight/dashboard.html` - Main dashboard with KPIs
- Uses: `base/kpi_card.html`, `base/kpi_card_white.html` (KPI display)
- Links to: All detailed reports

**KPI Metrics:**
- Today's sales total
- Transaction count
- Top products
- Cash vs card ratio
- New customers acquired
- Low stock warnings

---

## 👤 User Management & Access

### User Accounts
**Feature Purpose:** Create & manage system users  
**Related Templates:**
- `settings/users.html` - User list
- `settings/profile.html` - Individual user profile (personal info, change password)
- Form uses: `base/partials/form_field.html`

**User Attributes:**
- Name, email, phone
- Role/permissions
- Store/location assignment
- Status (active/inactive)

**Access Control:** Role-based (admin, manager, staff, viewer)

---

### Permission & Roles
**Feature Purpose:** Control feature access by role  
**Related Templates:**
- `settings/users.html` - Role assignment during user creation
- Typically managed in admin panel (not in template screenshots)

**Typical Roles:**
- Admin: Full access
- Manager: Store/area level
- Staff: Limited to POS or assigned features
- Viewer: Reports only (read-only)

---

### Profile & Password
**Feature Purpose:** User profile management  
**Related Templates:**
- `settings/profile.html` - View/edit personal profile
- View/change avatar
- Change password (form)
- Account preferences (language, theme, etc.)

---

## ⚙️ System & Administration

### System Settings
**Feature Purpose:** Configure system parameters  
**Related Templates:**
- `settings/settings.html` - General settings hub
- `settings/system_status.html` - System health dashboard
- `settings/business_settings.html` - Business configuration
- `settings/business_form_general.html` - Business info form
- `settings/business_profile.html` - Business branding

**Configuration Items:**
- Currency, language, timezone
- Business logo & branding
- System hours/holidays
- Backup settings
- API integrations

---

### Business Profile
**Feature Purpose:** Maintain company information  
**Related Templates:**
- `settings/business_settings.html` - Settings hub
- `settings/business_form_general.html` - Edit business info (company name, tax ID, etc.)
- `settings/business_profile.html` - View/display company info
- `settings/business_feature_matrix.html` - Feature enablement/licensing

**Used For:**
- Invoice/receipt headers
- Business registration info
- Multi-branch management

---

### System Monitoring
**Feature Purpose:** Monitor system health & performance  
**Related Templates:**
- `settings/system_status.html` - Database, API, storage status
- Shows: Uptime, backup status, user count
- Alert: If issues detected

---

### Global Search
**Feature Purpose:** Find anything across the system  
**Related Templates:**
- `settings/search.html` - Global search interface
- Available from: navbar in `base/navbar.html`
- Searches: Products, customers, vendors, reports, etc.

---

## 🔐 Authentication & Access

### Login
**Feature Purpose:** User authentication  
**Related Templates:**
- `auth/login.html` - Login form
- Fields: Email/username, password
- Features: "Remember me", forgot password link
- On success: Redirects to `sales_insight/dashboard.html`

---

### Registration
**Feature Purpose:** Create new user account  
**Related Templates:**
- `auth/register.html` - Registration form
- Fields: Name, email, password, confirm password
- Terms acceptance checkbox
- On success: Redirects to login or dashboard

---

### Error Handling
**Feature Purpose:** Handle access denied & not found errors  
**Related Templates:**
- `etc/error_403.html` - Permission denied
- `etc/error_404.html` - Page not found
- `etc/error_500.html` - Server error
- In navbar: Links back to home, contact support

---

## 🧩 Information Pages

### About System
**Feature Purpose:** Display system information  
**Related Templates:**
- `settings/about.html` - System version, credits, license
- Links to: `settings/contact.html`

### Contact & Support  
**Feature Purpose:** Get help & submit tickets  
**Related Templates:**
- `settings/contact.html` - Contact info, support form
- Links to: `settings/about.html`, FAQs

---

## 🎯 User Journey Examples

### Manager's Daily Workflow
```
1. Login (auth/login.html)
2. Dashboard (sales_insight/dashboard.html) → View KPIs
3. Check low stock (inventory/stock_overview.html)
   → Low stock alert? → Go to (reports/report_inventory_low.html)
   → Create PO in (inventory/stock_purchasing.html)
4. Review sales (reports/sales_report.html)
5. Check pending approvals (inventory/stock_opname_approvals.html)
6. Profile update (settings/profile.html)
7. Logout
```

### Cashier's POS Workflow
```
1. Login (auth/login.html)
2. Go to POS (sales_insight/pos.html)
3. Select products → Search customer → Apply discount
4. Process payment → Complete transaction
5. View receipt → Return to POS
6. End of day → Manager reviews (reports/transaction_summary.html)
```

### Inventory Staff Workflow
```
1. Login → Stock opname needed?
2. (inventory/stock_opname_locations.html) → Select location
3. (inventory/stock_opname_form.html) → Enter counts
4. Submit → Manager reviews (inventory/stock_opname_approvals.html)
5. Approve → Generate stock movements (inventory/stock_movement.html)
6. Track in (reports/report_inventory_log.html)
```

### Accountant's Workflow
```
1. Login → Dashboard (sales_insight/dashboard.html)
2. Financial reports (sales_insight/financial_reports.html)
3. Detail P&L (reports/report_profit_loss_detail.html)
4. Sales breakdown (reports/report_sales_by_product.html)
5. Inventory valuation (reports/report_inventory_stock.html)
6. Export all reports → Accounting system
```

---

**Usage:** Reference this map when building connections between features or understanding the data flow through templates.
