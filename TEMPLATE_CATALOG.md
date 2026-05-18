# 📋 LUMRA ERP - Template Catalog
**Complete Inventory of 102 HTML Files**  
*Generated: April 10, 2026*

---

## 📑 Table of Contents
1. [Base Components](#base-components) - Shared UI building blocks
2. [Authentication](#authentication) - Login/Register flows
3. [Inventory Management](#inventory-management) - 16 templates
4. [Sales & POS](#sales--pos-module) - 7 templates
5. [Production/Recipes](#productionrecipes-module) - 3 templates
6. [Marketing Management](#marketing-management-module) - 5 templates
7. [Master Data](#master-data--configuration-module) - 13 templates
8. [Reports & Analytics](#reports--analytics-module) - 20 templates
9. [Messages & Notifications](#messages--notifications) - 2 templates
10. [Settings & System](#settings--system-administration) - 10 templates
11. [Error Pages](#error-pages) - 3 templates

---

## 🏗️ Base Components
**Location:** `lumra_config/templates/base/`  
*Reusable UI components & layout templates inherited by all pages*

| File | Purpose | Used By |
|------|---------|---------|
| **base.html** | Master layout template; Root HTML structure with CMS blocks (title, extra_head, extra_css, content) | ALL pages inherit |
| **navbar.html** | Top navigation bar with search, user menu, notifications | All authenticated pages |
| **sidebar.html** | Left sidebar navigation with module menu items | All authenticated pages |
| **sidebar_item.html** | Individual navigation menu item component | sidebar.html |
| **sidebar_right.html** | Right sidebar (alternative panel, usually for filters/settings) | Some dashboard pages |
| **footer.html** | Page footer with copyright & links | Authentication pages |
| **alert.html** | Full-page alert component wrapper | Error pages, notifications |
| **alert_inner.html** | Inner alert message component | alert.html, modal windows |
| **approval_modal.html** | Modal for approval workflows (stock opname, requisitions) | Inventory feature pages |
| **kpi_card.html** | Dashboard KPI display card (dark theme) | dashboard.html |
| **kpi_card_inner.html** | Inner KPI card component (content wrapper) | kpi_card.html |
| **kpi_card_white.html** | Dashboard KPI display card (white theme) | dashboard.html |
| **partials/form_field.html** | Standard form field component (TextInput, Select, Textarea) | All form pages |
| **partials/bg_blob.html** | Decorative background blob SVG element | Login/Register pages |

---

## 🔐 Authentication
**Location:** `lumra_config/templates/lumra_pages/auth/`  
*User authentication & access control flows*

| File | Purpose | Features | Connects To |
|------|---------|----------|-------------|
| **login.html** | Login page with email/password form | - Form validation<br/>- "Remember me" option<br/>- Forgot password link | Dashboard (on success) |
| **register.html** | User registration page | - Email, password, confirm password<br/>- Terms acceptance checkbox<br/>- Form validation | Dashboard/Login (on success) |

---

## 📦 Inventory Management Module
**Location:** `lumra_config/templates/lumra_pages/inventory/`  
*Product, stock, supplier, and purchasing management*

### Core Inventory Views (6 templates)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **products.html** | Product list/dashboard view | - Table of all products<br/>- Stock aggregation by location<br/>- Quick actions (edit, delete)<br/>- Filters & search | product_details.html, product_list.html |
| **product_details.html** | Detailed product view | - Product metadata (code, category, unit)<br/>- Current stock by location<br/>- Pricing info<br/>- Movement history | products.html |
| **product_list.html** | Alternative product listing (paginated) | - Grid/list view toggle<br/>- Bulk actions<br/>- Import/export buttons | products.html, product_details.html |
| **stock_overview.html** | Dashboard for stock status | - Low stock alerts<br/>- Stock value summary<br/>- Location-wise breakdown<br/>- Quick actions | stock_movement.html, stock_planning.html |
| **stock_movement.html** | Stock transaction log viewer | - All stock movements chronologically<br/>- Filter by date, location, type<br/>- Export functionality | add_stock_movement.html, stock_overview.html |
| **stock_planning.html** | Stock allocation & planning view | - Forecast vs actual<br/>- Reorder recommendations<br/>- Allocation by location<br/>- Planning submission | stock_purchasing.html, stock_movement.html |

### Stock Opname (Physical Count) (5 templates)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **stock_opname_locations.html** | Select locations for stock count | - Location checklist<br/>- Start new count button<br/>- View past counts | stock_opname_form.html |
| **stock_opname_form.html** | Physical count data entry | - Product list by location<br/>- Current vs counted quantity<br/>- Notes field<br/>- Submit for approval | stock_opname_approvals.html, stock_opname_locations.html |
| **stock_opname_approvals.html** | List of stock counts awaiting approval | - Pending counts table<br/>- Approve/reject actions<br/>- View discrepancies | stock_opname_approval_detail.html |
| **stock_opname_approval_detail.html** | Detailed view of opname for approval | - Product-level discrepancies<br/>- Approve/reject buttons<br/>- Comments field<br/>- Variance analysis | stock_opname_approvals.html |
| **stock_opname_locations.html** |  Locations list for stock opname reference | (in master_data) | - stock_opname_form.html |

### Stock Movement (1 template)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **add_stock_movement.html** | Create new stock movement (adjustment, transfer, damage) | - Movement type selector<br/>- From/to location<br/>- Product selection<br/>- Quantity & notes<br/>- Reason codes | stock_movement.html, stock_overview.html |
| **stock_movement_form.html** | Alternative form for stock adjustments | - Batch processing<br/>- Template loading<br/>- Validation rules | add_stock_movement.html |

### Purchasing & Suppliers (4 templates)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **stock_purchasing.html** | Purchase order management | - PO list<br/>- Create/Edit PO<br/>- Supplier selection<br/>- Expected delivery tracking<br/>- Approval workflow | supplier_price_list.html, stock_movement.html |
| **supplier_price_list.html** | Supplier pricing list | - Price by supplier/product<br/>- Effective dates<br/>- Edit/delete actions<br/>- Price comparison table | supplier_price_form.html |
| **supplier_price_form.html** | Add/edit supplier pricing | - Supplier selector<br/>- Product selector<br/>- Price input<br/>- Effective date range<br/>- MOQ (minimum order qty) | supplier_price_list.html |
| **supplier_price_confirm_delete.html** | Confirmation modal for price deletion | - Show price details<br/>- Confirm/cancel buttons | supplier_price_list.html |

---

## 💰 Sales & POS Module
**Location:** `lumra_config/templates/lumra_pages/sales_insight/`  
*Point-of-sale, transactions, and sales monitoring*

| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **pos.html** | Point of Sale interface | - Product selection (search/category filter)<br/>- Shopping cart with totals<br/>- Payment method selector<br/>- Customer lookup<br/>- Discount application<br/>- Real-time total calculation | dashboard.html, sales_intelligence.html |
| **dashboard.html** | Main dashboard with KPIs | - Today's sales total<br/>- Transaction count<br/>- Top products<br/>- KPI cards with trends<br/>- Quick links to features | pos.html, sales_performance.html |
| **sales_intelligence.html** | Sales analytics overview | - Sales by time period<br/>- Product performance ranking<br/>- Customer insights<br/>- Trend charts<br/>- Drill-down capabilities | sales_performance.html, trends_analysis.html |
| **sales_performance.html** | Detailed sales performance metrics | - Daily/weekly/monthly comparison<br/>- Channel breakdown<br/>- Staff performance (if applicable)<br/>- Target vs actual | sales_intelligence.html, financial_reports.html |
| **financial_reports.html** | Financial overview dashboard | - Revenue summary<br/>- Expense breakdown (if available)<br/>- Profit summary<br/>- Cash flow indicators<br/>- Period selector | sales_report.html, report_profit_loss_detail.html |
| **market_insights.html** | Market analysis dashboard | - Market trends<br/>- Competitor data (if available)<br/>- Customer demographics<br/>- Seasonal patterns | trends_analysis.html |
| **trends_analysis.html** | Detailed trend analysis | - Historical data visualization<br/>- Forecast projection<br/>- Anomaly detection<br/>- Export functionality | market_insights.html, financial_reports.html |

---

## 🏭 Production/Recipes Module
**Location:** `lumra_config/templates/lumra_pages/production/`  
*Recipe management for manufacturing/food service*

| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **recipe_list.html** | Recipe catalog/list view | - All recipes list<br/>- Search & filter<br/>- Create new button<br/>- Edit/delete/view actions<br/>- Cost calculation display | recipe_detail.html, recipe_form.html |
| **recipe_form.html** | Create/edit recipe | - Recipe name & code<br/>- Ingredient list with quantities<br/>- Unit selector<br/>- Yield amount<br/>- Cost auto-calculation<br/>- Save & cancel buttons | recipe_list.html, recipe_detail.html |
| **recipe_detail.html** | View detailed recipe | - Recipe ingredients breakdown<br/>- Total cost calculation<br/>- Usage history<br/>- Edit/delete buttons<br/>- Print functionality | recipe_list.html, recipe_form.html |

---

## 📢 Marketing Management Module
**Location:** `lumra_config/templates/lumra_pages/marketing/`  
*Campaigns, discounts, and loyalty programs*

| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **campaign.html** | Campaign list view | - All active/past campaigns<br/>- Campaign duration<br/>- Performance metrics<br/>- Create/edit/delete<br/>- Status indicators | campaign_list.html, add_campaign.html |
| **campaign_list.html** | Alternative campaign listing (paginated) | - Searchable campaign list<br/>- Filter by status/date<br/>- Bulk actions | campaign.html, add_campaign.html |
| **add_campaign.html** | Create new campaign | - Campaign name & description<br/>- Start/end date<br/>- Target audience<br/>- Budget allocation<br/>- Campaign type selector | campaign.html, campaign_list.html |
| **discount.html** | Discount management view | - Active discounts list<br/>- Discount amount/percentage<br/>- Eligibility rules<br/>- Create/edit/delete | Marketing dashboard |
| **loyalty_members.html** | Loyalty program member list | - Member list with points<br/>- Tier information<br/>- Recent transactions<br/>- Redeem points interface<br/>- Add member button | Marketing dashboard |

---

## 🗂️ Master Data & Configuration Module
**Location:** `lumra_config/templates/lumra_pages/master_data/`  
*Core reference data: categories, units, vendors, customers, locations*

### Categories (2 templates)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **categories_list.html** | Product categories list | - Categories with parent/child hierarchy<br/>- Create/edit/delete<br/>- Reorder (drag-drop?)<br/>- Bulk operations | category_form.html |
| **category_form.html** | Create/edit product category | - Category name<br/>- Parent category selector<br/>- Description<br/>- Status toggle<br/>- Code field | categories_list.html |

### Units of Measurement (2 templates)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **units_list.html** | Units of measurement list | - Unit name & symbol<br/>- Conversion rules (if applicable)<br/>- Create/edit/delete buttons | unit_form.html |
| **unit_form.html** | Create/edit unit | - Unit name input<br/>- Symbol/abbreviation<br/>- Description<br/>- Status toggle | units_list.html |

### Vendors/Suppliers (3 templates)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **vendors_list.html** | Vendor/supplier list | - Vendor name, contact, code<br/>- Create/edit/delete<br/>- Search & filter<br/>- Performance rating | vendor_list.html, vendor_form.html |
| **vendor_list.html** | Alternative vendor listing (paginated) | - Vendor grid/list view<br/>- Filter by active status<br/>- Contact info display | vendors_list.html, vendor_form.html |
| **vendor_form.html** | Create/edit vendor | - Company name<br/>- Contact person & phone<br/>- Email & website<br/>- Address & tax number<br/>- Payment terms | vendors_list.html, vendor_list.html |

### Customers (5 templates)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **customers.html** | Main customer dashboard | - Customer count<br/>- Recent new customers<br/>- Top customers link<br/>- Quick action buttons | customers_list.html, customer_detail.html |
| **customers_list.html** | Paginated customer list | - Searchable customer table<br/>- Filter by status/segment<br/>- View/edit/delete actions | customers.html, customer_detail.html |
| **customer_detail.html** | Detailed customer view | - Customer profile info<br/>- Total purchase history<br/>- Loyalty points balance<br/>- Last purchase date<br/>- Contact preferences | customers_list.html, customer_form.html |
| **customer_form.html** | Create/edit customer | - Customer name<br/>- Email & phone<br/>- Address fields<br/>- Customer type (retail/wholesale)<br/>- Birth date (for promotions) | customers_list.html, customer_detail.html |
| **customer.html** | Alternative customer view | (Similar to customer_detail.html) | customers_list.html |

### Locations (2 templates)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **locations.html** | Locations/outlets list | - All store locations<br/>- Address & manager<br/>- Stock available at each<br/>- Create/edit/delete | location_list.html |
| **location_list.html** | Location inventory view | - Locations with current stock<br/>- Filter by region<br/>- Performance metrics | locations.html |

### Stock Opname Session View (1 template)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **stock_opname_session_detail.html** | Historical stock opname session | - Session summary<br/>- All counted items<br/>- Approved/rejected status<br/>- Audit trail | stock_opname_approvals.html |

---

## 📊 Reports & Analytics Module
**Location:** `lumra_config/templates/lumra_pages/reports/`  
*20 comprehensive reporting templates for business intelligence*

### Sales Reports (7 templates)
| File | Purpose | Data Shown | Export Options |
|------|---------|-----------|---|
| **sales_report.html** | Main sales report (customizable) | - Total sales by period<br/>- Product mix<br/>- Payment methods breakdown<br/>- Period-over-period comparison | PDF, Excel, CSV |
| **sales_history.html** | Complete transaction history | - All transactions chronologically<br/>- Customer name<br/>- Amount & payment method<br/>- Timestamp<br/>- Staff who processed | PDF, CSV |
| **sales_history_product.html** | Sales by product | - Product list with quantities sold<br/>- Revenue per product<br/>- Margin analysis<br/>- Trending status | PDF, Excel |
| **report_sales_by_outlet.html** | Sales performance by location | - Sales by store/location<br/>- Location rank<br/>- Target vs actual<br/>- Staff count per location | PDF, Excel |
| **report_sales_by_payment.html** | Payment method breakdown | - Cash vs card vs mobile<br/>- Refunds by method<br/>- Average transaction value<br/>- Payment failures | PDF, Excel |
| **report_sales_by_product.html** | Sales analysis by product | - Product ranking<br/>- Units sold<br/>- Revenue %<br/>- Profit margin | PDF, Excel |
| **sales_report_after.html** | Post-transaction summary report | (Enhanced version with additional metrics) | PDF, Excel, CSV |

### Inventory Reports (4 templates)
| File | Purpose | Data Shown | Use Case |
|------|---------|-----------|----------|
| **report_inventory_stock.html** | Current stock levels | - All products with current qty<br/>- Stock value (cost)<br/>- Min/max thresholds<br/>- Days supply | Inventory audit |
| **report_inventory_log.html** | Stock transaction log | - All movements: in/out/adjust<br/>- Timestamp<br/>- Reason codes<br/>- Running balance | Transaction audit |
| **report_inventory_low.html** | Low stock alert report | - Products below minimum qty<br/>- Reorder level crossed<br/>- Recommended PO qty<br/>- Priority ranking | Purchase planning |
| **stock_overview.html** | (in inventory/) Stock summary | - Total inventory value<br/>- By location breakdown<br/>- Stock age distribution<br/>- Obsolescence risk | Executive dashboard |

### Financial Reports (2 templates)
| File | Purpose | Data Shown | Frequency |
|------|---------|-----------|-----------|
| **report_profit_loss_detail.html** | Detailed P&L statement | - Revenue by category<br/>- COGS calculation<br/>- Operating expenses<br/>- Net profit<br/>- Margin %, Ratio analysis | Monthly/Quarterly |
| **financial_reports.html** | (in sales_insight/) Executive financial dashboard | - Revenue trend<br/>- Profit/loss visual<br/>- Cash position<br/>- Key ratios | Daily |

### Operational Reports (4 templates)
| File | Purpose | Data Shown | Use Case |
|------|---------|-----------|----------|
| **requisition_report.html** | Stock requisition history | - All requisitions submitted<br/>- Approval status<br/>- Fulfillment status<br/>- Pending items | Supply chain tracking |
| **purchasing_report.html** | Purchase order summary | - PO by vendor<br/>- Spending by vendor<br/>- Delivery performance<br/>- Price trends | Vendor management |
| **transfer_report.html** | Stock transfer report | - Inter-location transfers<br/>- Transfer status<br/>- Timing analysis<br/>- Receiving confirmation | Distribution tracking |
| **transaction_summary.html** | Summary of all transactions | - Daily/weekly summary<br/>- Transaction counts<br/>- Value totals<br/>- Exception items | Executive summary |

### Activity & Support (2 templates)
| File | Purpose | Data Shown | Audience |
|------|---------|-----------|----------|
| **activity_log.html** | User activity audit log | - Login/logout times<br/>- Transaction created/modified<br/>- Data changes with before/after<br/>- User & timestamp | Audit/compliance |
| **base_report.html** | Base template for custom reports | - Report framework<br/>- Standard filters<br/>- Export buttons<br/>- Date range picker | Template for new reports |

### Report Base & Listing (1 template)
| File | Purpose | Features |
|------|---------|----------|
| **reporting.html** | Report selection/hub page | - Link to all reports<br/>- Report categories<br/>- Recently accessed reports<br/>- Most used reports |

---

## 💬 Messages & Notifications
**Location:** `lumra_config/templates/lumra_pages/messages/`  
*Internal messaging and notification system*

| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **inbox.html** | User message inbox | - Message list<br/>- Mark read/unread<br/>- Delete messages<br/>- Message threads<br/>- Search & filter | notification.html |
| **notification.html** | Notification center | - Real-time alerts<br/>- Notification history<br/>- Filter by type<br/>- Mark as read bulk<br/>- Clear all option | inbox.html |

---

## ⚙️ Settings & System Administration
**Location:** `lumra_config/templates/lumra_pages/settings/`  
*System configuration, user management, business settings*

### User & Access Management (2 templates)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **users.html** | User list & management | - All system users<br/>- Role assignment<br/>- Active/inactive toggle<br/>- Last login<br/>- Create/edit/delete user<br/>- Permission matrix link | profile.html |
| **profile.html** | User profile page (Personal) | - User info (name, email, phone)<br/>- Change password<br/>- Avatar upload<br/>- Account preferences<br/>- Two-factor auth setup | users.html |

### Business Configuration (4 templates)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **business_settings.html** | Main business configuration | - Dashboard for all settings<br/>- Quick links to detail pages<br/>- Logo/branding upload<br/>- Business hours<br/>- Currency settings | business_form_general.html |
| **business_form_general.html** | General business info form | - Company name<br/>- Registration number<br/>- Tax ID<br/>- Industry classification<br/>- Contact details<br/>- Website URL | business_settings.html, business_profile.html |
| **business_profile.html** | Business profile view | - Company info display<br/>- Logo/branding showcase<br/>- Branch overview<br/>- Edit button | business_settings.html |
| **business_feature_matrix.html** | Feature enablement matrix | - Module activation toggles<br/>- Feature licensing<br/>- Add-on purchase links<br/>- Usage statistics per feature | business_settings.html |

### System & Information (3 templates)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **system_status.html** | System health dashboard | - Database status<br/>- API endpoint status<br/>- Storage usage<br/>- User session count<br/>- Last backup timestamp | business_settings.html |
| **settings.html** | General settings hub | - Navigation to all settings<br/>- Display preferences<br/>- Notification rules<br/>- Export/backup options<br/>- System logs link | business_settings.html, system_status.html |
| **search.html** | Global search interface | - Search across all modules<br/>- Result categorization<br/>- Recent searches<br/>- Quick filters | All pages with navbar |

### Information Pages (3 templates)
| File | Purpose | Features | Related Files |
|------|---------|----------|---------------|
| **about.html** | About system page | - System version<br/>- Build information<br/>- Credits<br/>- License information<br/>- Support links | contact.html, settings.html |
| **contact.html** | Contact/support page | - Support contact info<br/>- Support ticket submission<br/>- FAQ links<br/>- Social media links | about.html, settings.html |

---

## ❌ Error Pages
**Location:** `lumra_config/templates/lumra_pages/etc/`  
*HTTP error handling pages*

| File | HTTP Status | Message | Suggests |
|------|----------|---------|----------|
| **error_403.html** | 403 | Access Denied/Forbidden | - Link to home<br/>- Permission request form<br/>- Contact admin |
| **error_404.html** | 404 | Page Not Found | - Search box<br/>- Navigation menu<br/>- Report broken link |
| **error_500.html** | 500 | Server Error | - Retry button<br/>- Contact support<br/>- Status page link |

---

## 🔗 Component Hierarchy
```
base.html (Root layout)
├── navbar.html
│   ├── Search modal
│   └── User dropdown menu
├── sidebar.html
│   ├── sidebar_item.html (repeated for each menu)
│   └── Module links
├── sidebar_right.html (optional on some pages)
├── [Page content block]
└── footer.html (Authentication pages only)

All lumra_pages/*.html extend base.html
├── Form pages use: partials/form_field.html
├── Modals use: approval_modal.html, alert_inner.html
├── Dashboards use: kpi_card.html, kpi_card_inner.html, kpi_card_white.html
└── Error pages use: alert.html, alert_inner.html
```

---

## 📝 Notes
- **Total Templates:** 102 files
- **Base Components:** 14 files
- **Authentication:** 2 files
- **Inventory:** 16 files
- **Sales/POS:** 7 files
- **Production:** 3 files
- **Marketing:** 5 files
- **Master Data:** 13 files
- **Reports:** 20 files
- **Messages:** 2 files
- **Settings:** 10 files
- **Errors:** 3 files

- **Theme:** Emerald Odyssey (Glassmorphism, Tailwind CSS + Alpine.js)
- **Framework:** Django with Tailwind CSS
- **JavaScript:** Alpine.js for reactive components
- **Responsive:** Mobile-first, optimized for mobile & desktop
