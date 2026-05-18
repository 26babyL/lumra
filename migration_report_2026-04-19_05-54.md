# Migration Report — 19 April 2026 05:54

## Summary

| Status | Count |
|--------|-------|
| ✅ OK    | 185 |
| ⚠️ Warn  | 7 |
| ❌ Error | 0 |
| **Total** | **192** |

## Per Module

| Module | OK | Warn | Error | Total |
|--------|----|------|-------|-------|
| Accounting | 13 | 0 | 0 | 13 |
| Inventory | 27 | 0 | 0 | 27 |
| Other | 76 | 2 | 0 | 78 |
| Production | 11 | 3 | 0 | 14 |
| Reports | 23 | 2 | 0 | 25 |
| Sales | 14 | 0 | 0 | 14 |
| Settings | 21 | 0 | 0 | 21 |

## Templates Butuh Fix

### ⚠️ `customer_detail.html` (Other)
- Pattern : Form + Dropdown
- Vars    : -
- Issues  : NO_BLOCK
  - 🟡 **NO_BLOCK**: Template punya Alpine/JS tapi tidak ada block scripts

### ⚠️ `recipe_detail.html` (Production)
- Pattern : Form + Dropdown
- Vars    : -
- Issues  : NO_BLOCK
  - 🟡 **NO_BLOCK**: Template punya Alpine/JS tapi tidak ada block scripts

### ⚠️ `recipe_form.html` (Production)
- Pattern : Form + Dropdown
- Vars    : -
- Issues  : NO_BLOCK
  - 🟡 **NO_BLOCK**: Template punya Alpine/JS tapi tidak ada block scripts

### ⚠️ `recipe_list.html` (Production)
- Pattern : Form + Dropdown
- Vars    : -
- Issues  : NO_BLOCK
  - 🟡 **NO_BLOCK**: Template punya Alpine/JS tapi tidak ada block scripts

### ⚠️ `base_report.html` (Reports)
- Pattern : Simple List
- Vars    : -
- Issues  : NO_BLOCK
  - 🟡 **NO_BLOCK**: Template punya Alpine/JS tapi tidak ada block scripts

### ⚠️ `reporting.html` (Reports)
- Pattern : Chart.js Data
- Vars    : -
- Issues  : NO_BLOCK
  - 🟡 **NO_BLOCK**: Template punya Alpine/JS tapi tidak ada block scripts

### ⚠️ `dashboard.html` (Other)
- Pattern : Chart.js Data
- Vars    : -
- Issues  : NO_BLOCK
  - 🟡 **NO_BLOCK**: Template punya Alpine/JS tapi tidak ada block scripts

## Templates Sudah OK

- ✅ `accounts_payable.html` (Accounting)
- ✅ `accounts_receivable.html` (Accounting)
- ✅ `balance_sheet.html` (Accounting)
- ✅ `cash_flow.html` (Accounting)
- ✅ `chart_of_accounts.html` (Accounting)
- ✅ `chart_of_accounts_form.html` (Accounting)
- ✅ `general_ledger.html` (Accounting)
- ✅ `journal_entry_detail.html` (Accounting)
- ✅ `journal_entry_form.html` (Accounting)
- ✅ `journal_entry_list.html` (Accounting)
- ✅ `payment_voucher_form.html` (Accounting)
- ✅ `profit_loss_statement.html` (Accounting)
- ✅ `trial_balance.html` (Accounting)
- ✅ `forgot_password.html` (Other)
- ✅ `lock_screen.html` (Other)
- ✅ `login.html` (Other)
- ✅ `register.html` (Other)
- ✅ `reset_password.html` (Other)
- ✅ `session_expired.html` (Other)
- ✅ `two_factor.html` (Other)
- ✅ `verify_email.html` (Other)
- ✅ `error_403.html` (Other)
- ✅ `error_404.html` (Other)
- ✅ `error_500.html` (Other)
- ✅ `error_maintenance.html` (Other)
- ✅ `error_session_expired.html` (Other)
- ✅ `add_stock_movement.html` (Inventory)
- ✅ `adjustment_reasons.html` (Inventory)
- ✅ `batch_detail.html` (Inventory)
- ✅ `batch_form.html` (Inventory)
- ✅ `batch_list.html` (Inventory)
- ✅ `expiry_tracking.html` (Inventory)
- ✅ `product_details.html` (Inventory)
- ✅ `product_list.html` (Inventory)
- ✅ `products.html` (Inventory)
- ✅ `requisition_detail.html` (Inventory)
- ✅ `requisition_form.html` (Inventory)
- ✅ `requisition_list.html` (Inventory)
- ✅ `stock_movement.html` (Inventory)
- ✅ `stock_movement_form.html` (Inventory)
- ✅ `stock_opname_approval_detail.html` (Inventory)
- ✅ `stock_opname_approvals.html` (Inventory)
- ✅ `stock_opname_form.html` (Inventory)
- ✅ `stock_opname_locations.html` (Inventory)
- ✅ `stock_overview.html` (Inventory)
- ✅ `stock_planning.html` (Inventory)
- ✅ `stock_purchasing.html` (Inventory)
- ✅ `supplier_evaluation.html` (Inventory)
- ✅ `supplier_price_confirm_delete.html` (Inventory)
- ✅ `supplier_price_form.html` (Inventory)
- ✅ `supplier_price_list.html` (Inventory)
- ✅ `warehouse_zone_form.html` (Inventory)
- ✅ `warehouse_zones.html` (Inventory)
- ✅ `add_campaign.html` (Other)
- ✅ `campaign.html` (Other)
- ✅ `campaign_list.html` (Other)
- ✅ `customer_segment_form.html` (Other)
- ✅ `customer_segment_list.html` (Other)
- ✅ `discount.html` (Other)
- ✅ `loyalty_members.html` (Other)
- ✅ `promotion_calendar.html` (Other)
- ✅ `voucher_claim_log.html` (Other)
- ✅ `voucher_form.html` (Other)
- ✅ `voucher_list.html` (Other)
- ✅ `bank_account_form.html` (Other)
- ✅ `bank_accounts.html` (Other)
- ✅ `categories_list.html` (Other)
- ✅ `category_form.html` (Other)
- ✅ `customer.html` (Other)
- ✅ `customer_form.html` (Other)
- ✅ `customers.html` (Other)
- ✅ `customers_list.html` (Other)
- ✅ `location_list.html` (Other)
- ✅ `locations.html` (Other)
- ✅ `payment_terms_form.html` (Other)
- ✅ `payment_terms_list.html` (Other)
- ✅ `reason_codes.html` (Other)
- ✅ `stock_opname.html` (Other)
- ✅ `stock_opname_session_detail.html` (Other)
- ✅ `tags_list.html` (Other)
- ✅ `tax_form.html` (Other)
- ✅ `tax_list.html` (Other)
- ✅ `unit_form.html` (Other)
- ✅ `units_list.html` (Other)
- ✅ `vendor_form.html` (Other)
- ✅ `vendor_list.html` (Other)
- ✅ `vendors_list.html` (Other)
- ✅ `broadcast.html` (Other)
- ✅ `compose.html` (Other)
- ✅ `inbox.html` (Other)
- ✅ `message_detail.html` (Other)
- ✅ `message_templates.html` (Other)
- ✅ `notification.html` (Other)
- ✅ `step_business.html` (Other)
- ✅ `step_category.html` (Other)
- ✅ `step_complete.html` (Other)
- ✅ `step_location.html` (Other)
- ✅ `welcome.html` (Other)
- ✅ `print_base.html` (Other)
- ✅ `print_credit_note.html` (Other)
- ✅ `print_delivery_note.html` (Other)
- ✅ `print_invoice.html` (Other)
- ✅ `print_packing_slip.html` (Other)
- ✅ `print_payment_receipt.html` (Other)
- ✅ `print_production_order.html` (Other)
- ✅ `print_purchase_order.html` (Other)
- ✅ `print_quotation.html` (Other)
- ✅ `print_receipt.html` (Other)
- ✅ `print_sales_order.html` (Other)
- ✅ `print_stock_opname.html` (Other)
- ✅ `bom_detail.html` (Production)
- ✅ `bom_form.html` (Production)
- ✅ `bom_list.html` (Production)
- ✅ `finished_goods_receipt.html` (Production)
- ✅ `material_consumption.html` (Production)
- ✅ `production_costing.html` (Production)
- ✅ `production_order_detail.html` (Production)
- ✅ `production_order_form.html` (Production)
- ✅ `production_order_list.html` (Production)
- ✅ `production_scheduling.html` (Production)
- ✅ `production_waste.html` (Production)
- ✅ `activity_log.html` (Reports)
- ✅ `purchasing_report.html` (Reports)
- ✅ `report_activity_log.html` (Reports)
- ✅ `report_customer_lifetime.html` (Reports)
- ✅ `report_expiry.html` (Reports)
- ✅ `report_inventory_age.html` (Reports)
- ✅ `report_inventory_log.html` (Reports)
- ✅ `report_inventory_low.html` (Reports)
- ✅ `report_inventory_stock.html` (Reports)
- ✅ `report_production.html` (Reports)
- ✅ `report_profit_loss_detail.html` (Reports)
- ✅ `report_sales_by_outlet.html` (Reports)
- ✅ `report_sales_by_payment.html` (Reports)
- ✅ `report_sales_by_product.html` (Reports)
- ✅ `report_sales_summary.html` (Reports)
- ✅ `report_staff_performance.html` (Reports)
- ✅ `requisition_report.html` (Reports)
- ✅ `sales_history.html` (Reports)
- ✅ `sales_history_product.html` (Reports)
- ✅ `sales_report.html` (Reports)
- ✅ `sales_report_after.html` (Reports)
- ✅ `transaction_summary.html` (Reports)
- ✅ `transfer_report.html` (Reports)
- ✅ `invoice_detail.html` (Sales)
- ✅ `invoice_form.html` (Sales)
- ✅ `invoice_list.html` (Sales)
- ✅ `payment_form.html` (Sales)
- ✅ `payment_list.html` (Sales)
- ✅ `retur_detail.html` (Sales)
- ✅ `retur_form.html` (Sales)
- ✅ `retur_list.html` (Sales)
- ✅ `quotation_detail.html` (Sales)
- ✅ `quotation_form.html` (Sales)
- ✅ `quotation_list.html` (Sales)
- ✅ `sales_order_detail.html` (Sales)
- ✅ `sales_order_form.html` (Sales)
- ✅ `sales_order_list.html` (Sales)
- ✅ `financial_reports.html` (Other)
- ✅ `market_insights.html` (Other)
- ✅ `pos.html` (Other)
- ✅ `sales_intelligence.html` (Other)
- ✅ `sales_performance.html` (Other)
- ✅ `trends_analysis.html` (Other)
- ✅ `about.html` (Settings)
- ✅ `api_keys.html` (Settings)
- ✅ `backup_restore.html` (Settings)
- ✅ `business_feature_matrix.html` (Settings)
- ✅ `business_form_general.html` (Settings)
- ✅ `business_profile.html` (Settings)
- ✅ `business_settings.html` (Settings)
- ✅ `contact.html` (Settings)
- ✅ `email_settings.html` (Settings)
- ✅ `notification_settings.html` (Settings)
- ✅ `numbering_settings.html` (Settings)
- ✅ `permission_matrix.html` (Settings)
- ✅ `profile.html` (Settings)
- ✅ `role_form.html` (Settings)
- ✅ `roles.html` (Settings)
- ✅ `search.html` (Settings)
- ✅ `settings.html` (Settings)
- ✅ `system_status.html` (Settings)
- ✅ `user_list.html` (Settings)
- ✅ `user_roles_permissions.html` (Settings)
- ✅ `users.html` (Settings)