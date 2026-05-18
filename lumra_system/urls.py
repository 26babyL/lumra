# urls.py — Lumra ERP · Restructured with Clean Architecture
from django.contrib import admin
from django.urls import path, include
from django.utils.module_loading import import_string
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from lumra_config import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def lazy_view(dotted_path):
    """Lazy-import a view callable to avoid circular imports at startup."""
    def _callable(request, *args, **kwargs):
        view = import_string(dotted_path)
        return view(request, *args, **kwargs)
    return _callable


urlpatterns = [

    # =========================================================================
    # JWT AUTHENTICATION ENDPOINTS
    # =========================================================================
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # =========================================================================
    # ADMIN
    # =========================================================================
    path('admin/', admin.site.urls),

    # =========================================================================
    # LEGACY REDIRECTS  (keep for backward-compat, never remove silently)
    # =========================================================================
    path('accounts/login/',         RedirectView.as_view(url='/auth/login/',    permanent=False)),
    path('customers/',              RedirectView.as_view(url='/master/customers/', permanent=False)),
    path('inventory/products/',     RedirectView.as_view(url='/master/products/', permanent=False)),
    path('inventory/products/<int:product_id>/',
         RedirectView.as_view(url='/master/products/%(product_id)s/', permanent=False)),

    # =========================================================================
    # DASHBOARD  (single source of truth: root '/')
    # =========================================================================
    path('',        lazy_view('lumra_config.sales.views.dashboard_view'), name='dashboard'),
    path('home/',   RedirectView.as_view(url='/', permanent=False)),   # alias → root

    # =========================================================================
    # NOTIFICATIONS
    # =========================================================================
    path('notification/',  lazy_view('lumra_config.sales.views.notification_view'), name='notification'),
    path('notifications/', RedirectView.as_view(url='/notification/', permanent=False), name='notifications'),
    path('notifications/', views.inbox, name='inbox_messages'),

    # =========================================================================
    # LOCATIONS
    # =========================================================================
    path('locations/', lazy_view('lumra_config.master_data.views.locations_view'), name='locations'),

    # =========================================================================
    # MASTER DATA
    #   Products · Categories · Units · Vendors · Customers · Stock Opname
    # =========================================================================

    # ----- Products (Birth Certificate of goods — static identity) -----------
    path('master/products/',
         lazy_view('lumra_config.master_data.views.products_view'),               name='products'),
    path('master/products/<int:product_id>/',
         lazy_view('lumra_config.master_data.views.product_detail_view'),         name='product_detail'),
    # CSV template download (anchor in products.html)
    path('master/products/import-template/',
         lazy_view('lumra_config.inventory.views.products_import_template'),
         name='products_import_template'),

    # ----- Categories --------------------------------------------------------
    path('master/categories/',
         lazy_view('lumra_config.master_data.views.categories_list'),             name='categories_list'),
    path('master/categories/add/',
         lazy_view('lumra_config.master_data.views.category_create'),             name='category_create'),
    path('master/categories/<int:pk>/edit/',
         lazy_view('lumra_config.master_data.views.category_update'),             name='category_update'),
    path('master/categories/<int:pk>/delete/',
         lazy_view('lumra_config.master_data.views.category_delete'),             name='category_delete'),

    # ----- Units of Measure --------------------------------------------------
    path('master/units/',
         lazy_view('lumra_config.master_data.views.units_list'),                  name='units_list'),
    path('master/units/add/',
         lazy_view('lumra_config.master_data.views.unit_create'),                 name='unit_create'),
    path('master/units/<int:pk>/edit/',
         lazy_view('lumra_config.master_data.views.unit_update'),                 name='unit_update'),
    path('master/units/<int:pk>/delete/',
         lazy_view('lumra_config.master_data.views.unit_delete'),                 name='unit_delete'),

    # ----- Vendors / Suppliers -----------------------------------------------
    path('master/vendors/',
         lazy_view('lumra_config.master_data.views.vendors_list'),                name='vendors_list'),
    path('master/vendors/add/',
         lazy_view('lumra_config.master_data.views.vendor_create'),               name='vendor_create'),
    path('master/vendors/<int:pk>/edit/',
         lazy_view('lumra_config.master_data.views.vendor_update'),               name='vendor_update'),
    path('master/vendors/<int:pk>/delete/',
         lazy_view('lumra_config.master_data.views.vendor_delete'),               name='vendor_delete'),

    # ----- Customers ---------------------------------------------------------
    path('master/customers/',
         lazy_view('lumra_config.master_data.views.customer_list'),               name='customer_list'),
    path('master/customers/add/',
         lazy_view('lumra_config.master_data.views.customer_create'),             name='customer_create'),
    path('master/customers/<int:pk>/',
         lazy_view('lumra_config.master_data.views.customer_detail'),             name='customer_detail'),
    path('master/customers/<int:pk>/edit/',
         lazy_view('lumra_config.master_data.views.customer_update'),             name='customer_edit'),
    path('master/customers/<int:pk>/delete/',
         lazy_view('lumra_config.master_data.views.customer_delete'),             name='customer_delete'),
    path('master/customers/<int:pk>/redeem/',
         lazy_view('lumra_config.master_data.views.customer_redeem_points'),      name='customer_redeem_points'),

    # ----- Stock Opname (physical count — lives in Master because it
    #       reconciles the master record against physical reality) -------------
    path('master/stock-opname/',
         lazy_view('lumra_config.master_data.views.stock_opname_locations'),      name='stock_opname_locations'),
    path('master/stock-opname/<int:location_id>/form/',
         lazy_view('lumra_config.master_data.views.stock_opname_form'),           name='stock_opname_form'),
    path('master/stock-opname/approvals/',
         lazy_view('lumra_config.master_data.views.stock_opname_approvals'),      name='stock_opname_approvals'),
    path('master/stock-opname/approvals/<int:session_id>/',
         lazy_view('lumra_config.master_data.views.stock_opname_approval_detail'),name='stock_opname_approval_detail'),

    # =========================================================================
    # INVENTORY  — "Vital Signs" layer
    #   Stock overview · Movement · Planning · Supplier Prices · Batch · Requisition
    # =========================================================================

    # ----- Stock Overview (Products Inventory) -------------------------------
    path('inventory/overview/',
         lazy_view('lumra_config.inventory.views.products'),                    name='inventory_overview'),
    path('inventory/products/',
         lazy_view('lumra_config.inventory.views.products'),                    name='products'),

    # ----- Stock Planning (demand forecasting, reorder points) ---------------
    path('inventory/planning/',
         lazy_view('lumra_config.inventory.views.stock_planning_view'),         name='stock_planning'),

    # ----- Stock Movement (in/out transactions) ------------------------------
    path('inventory/movement/',
         lazy_view('lumra_config.inventory.views.stock_movement_view'),         name='stock_movement'),
    path('inventory/movement/add/',
         lazy_view('lumra_config.inventory.views.add_stock_movement_view'),     name='add_stock_movement'),
    path('inventory/movement/export/',
         lazy_view('lumra_config.inventory.views.export_stock_movement'),
                                                              name='stock_movement_export'),

    # ----- Batch Operations (bulk stock adjustments) --------------------------
    path('inventory/batch/',
         lazy_view('lumra_config.inventory.views.batch_list'),                  name='batch_list'),
    path('inventory/batch/add/',
         lazy_view('lumra_config.inventory.views.batch_form'),                  name='batch_form'),
    path('inventory/batch/<int:pk>/edit/',
         lazy_view('lumra_config.inventory.views.batch_form'),                  name='batch_edit'),
    path('inventory/batch/<int:pk>/',
         lazy_view('lumra_config.inventory.views.batch_detail'),                name='batch_detail'),

    # ----- Expiry Tracking ---------------------------------------------------
    path('inventory/expiry/',
         lazy_view('lumra_config.inventory.views.expiry_tracking'),             name='expiry_tracking'),

    # ----- Requisitions (stock requests from departments) --------------------
    path('inventory/requisitions/',
         lazy_view('lumra_config.inventory.views.requisition_list'),            name='requisition_list'),
    path('inventory/requisitions/add/',
         lazy_view('lumra_config.inventory.views.requisition_form'),            name='requisition_form'),
    path('inventory/requisitions/<int:pk>/edit/',
         lazy_view('lumra_config.inventory.views.requisition_form'),            name='requisition_edit'),
    path('inventory/requisitions/<int:pk>/detail/',
         lazy_view('lumra_config.inventory.views.requisition_detail'),          name='requisition_detail'),

    # ----- Supplier Prices ---------------------------------------------------
    path('inventory/supplier-prices/',
         lazy_view('lumra_config.inventory.views.supplier_price_list'),         name='supplier_price_list'),
    path('inventory/supplier-prices/form/',
         lazy_view('lumra_config.inventory.views.supplier_price_form'),         name='add_supplier_price'),
    path('inventory/supplier-prices/<int:price_id>/delete/',
         lazy_view('lumra_config.inventory.views.supplier_price_delete'),       name='supplier_price_delete'),

    # ----- Warehouse Zones (location management) ---------------------------
    path('warehouse/zones/',
         lazy_view('lumra_config.inventory.views.warehouse_zones'),             name='warehouse_zones'),
    path('warehouse/zones/add/',
         lazy_view('lumra_config.inventory.views.warehouse_zone_form'),         name='warehouse_zone_form'),
    path('warehouse/zones/<int:pk>/edit/',
         lazy_view('lumra_config.inventory.views.warehouse_zone_form'),         name='warehouse_zone_edit'),

    # ----- Admin & Analytics -------------------------------------------------
    path('inventory/adjustment-reasons/',
         lazy_view('lumra_config.inventory.views.adjustment_reasons'),          name='adjustment_reasons'),
    path('inventory/supplier-evaluation/',
         lazy_view('lumra_config.inventory.views.supplier_evaluation'),         name='supplier_evaluation'),

    # =========================================================================
    # PRODUCTION  — Recipes & Bill of Materials
    # =========================================================================
    path('production/recipes/',
         lazy_view('lumra_config.production.views.recipe_list'),                 name='recipe_list'),
    path('production/recipes/form/',
         lazy_view('lumra_config.production.views.recipe_form'),                 name='add_recipe'),
    path('production/recipes/<int:recipe_id>/',
         lazy_view('lumra_config.production.views.recipe_detail'),               name='recipe_detail'),
    path('production/recipes/<int:recipe_id>/edit/',
         lazy_view('lumra_config.production.views.recipe_form'),                 name='edit_recipe'),
    path('production/recipes/<int:recipe_id>/delete/',
         lazy_view('lumra_config.production.views.recipe_delete'),               name='delete_recipe'),
    # backward-compat alias
    path('production/recipes/<int:recipe_id>/delete-legacy/',
         lazy_view('lumra_config.production.views.recipe_delete'),               name='recipe_delete'),

    path('production/bom/',
         lazy_view('lumra_config.production.views.bom_list'),                    name='bom_list'),
    path('production/bom/form/',
         lazy_view('lumra_config.production.views.bom_form'),                    name='bom_form'),
    path('production/bom/<int:pk>/',
         lazy_view('lumra_config.production.views.bom_detail'),                  name='bom_detail'),
    path('production/bom/<int:pk>/edit/',
         lazy_view('lumra_config.production.views.bom_form'),                    name='bom_edit'),

    path('production/order/',
         lazy_view('lumra_config.production.views.production_order_list'),       name='production_order_list'),
    path('production/order/form/',
         lazy_view('lumra_config.production.views.production_order_form'),       name='production_order_form'),
    path('production/order/<int:pk>/',
         lazy_view('lumra_config.production.views.production_order_detail'),     name='production_order_detail'),
    path('production/order/<int:pk>/edit/',
         lazy_view('lumra_config.production.views.production_order_form'),       name='production_order_edit'),
    path('production/scheduling/',
         lazy_view('lumra_config.production.views.production_scheduling'),       name='production_scheduling'),
    path('production/consumption/',
         lazy_view('lumra_config.production.views.material_consumption'),        name='material_consumption'),
    path('production/finished/',
         lazy_view('lumra_config.production.views.finished_goods_receipt'),      name='finished_goods_receipt'),
    path('production/costing/',
         lazy_view('lumra_config.production.views.production_costing'),          name='production_costing'),
    path('production/waste/',
         lazy_view('lumra_config.production.views.production_waste'),            name='production_waste'),

    path('rnd/',
         lazy_view('lumra_config.production.views.rnd_list'),                    name='rnd_list'),
    path('rnd/form/',
         lazy_view('lumra_config.production.views.rnd_form'),                    name='rnd_form'),
    path('rnd/<int:pk>/',
         lazy_view('lumra_config.production.views.rnd_detail'),                  name='rnd_detail'),
    path('rnd/<int:pk>/status/',
         lazy_view('lumra_config.production.views.rnd_status_update'),           name='rnd_status_update'),
    path('rnd/<int:pk>/promote/',
         lazy_view('lumra_config.production.views.rnd_promote'),                 name='rnd_promote'),
    path('rnd/<int:pk>/trial/new/',
         lazy_view('lumra_config.production.views.rnd_trial_new'),               name='rnd_trial_new'),

    # =========================================================================
    # SALES — Orders · Quotations · Invoices · Payments · Returns
    # =========================================================================
    path('sales/pos/',
         lazy_view('lumra_config.sales.views.pos_view'),                    name='pos'),
    path('sales/pos/create-order/',
         lazy_view('lumra_config.sales.views.pos_create_order'),            name='pos_create_order'),
    path('sales/pos/process/',
         lazy_view('lumra_config.sales.views.pos_process_transaction'),     name='pos_process'),
    
    # ----- Sales Orders ------------------------------------------------------
    path('sales/order/',
         lazy_view('lumra_config.sales.views.sales_order_list'),            name='sales_order_list'),
    path('sales/order/add/',
         lazy_view('lumra_config.sales.views.sales_order_form'),            name='sales_order_form'),
    path('sales/order/<int:pk>/',
         lazy_view('lumra_config.sales.views.sales_order_detail'),          name='sales_order_detail'),
    path('sales/order/<int:pk>/edit/',
         lazy_view('lumra_config.sales.views.sales_order_form'),            name='sales_order_edit'),
    
    # ----- Quotations --------------------------------------------------------
    path('sales/quotation/',
         lazy_view('lumra_config.sales.views.quotation_list'),              name='quotation_list'),
    path('sales/quotation/add/',
         lazy_view('lumra_config.sales.views.quotation_form'),              name='quotation_form'),
    path('sales/quotation/<int:pk>/',
         lazy_view('lumra_config.sales.views.quotation_detail'),            name='quotation_detail'),
    path('sales/quotation/<int:pk>/edit/',
         lazy_view('lumra_config.sales.views.quotation_form'),              name='quotation_edit'),
    
    # ----- Invoices ----------------------------------------------------------
    path('sales/invoice/',
         lazy_view('lumra_config.sales.views.invoice_list'),                name='invoice_list'),
    path('sales/invoice/add/',
         lazy_view('lumra_config.sales.views.invoice_form'),                name='invoice_form'),
    path('sales/invoice/<int:pk>/',
         lazy_view('lumra_config.sales.views.invoice_detail'),              name='invoice_detail'),
    path('sales/invoice/<int:pk>/edit/',
         lazy_view('lumra_config.sales.views.invoice_form'),                name='invoice_edit'),
    
    # ----- Payments ----------------------------------------------------------
    path('sales/payment/',
         lazy_view('lumra_config.sales.views.payment_list'),                name='payment_list'),
    path('sales/payment/add/',
         lazy_view('lumra_config.sales.views.payment_form'),                name='payment_form'),
    path('sales/payment/<int:pk>/edit/',
         lazy_view('lumra_config.sales.views.payment_form'),                name='payment_edit'),

    # ----- Print Documents ---------------------------------------------------
    path('print/invoice/<int:pk>/',
         lazy_view('lumra_config.print_app.views.print_invoice'),           name='print_invoice'),
    path('print/sales-order/<int:pk>/',
         lazy_view('lumra_config.print_app.views.print_sales_order'),       name='print_sales_order'),
    path('print/quotation/<int:pk>/',
         lazy_view('lumra_config.print_app.views.print_quotation'),         name='print_quotation'),
    path('print/purchase-order/<int:pk>/',
         lazy_view('lumra_config.print_app.views.print_purchase_order'),    name='print_purchase_order'),
    path('print/delivery-note/<int:pk>/',
         lazy_view('lumra_config.print_app.views.print_delivery_note'),     name='print_delivery_note'),
    path('print/packing-slip/<int:pk>/',
         lazy_view('lumra_config.print_app.views.print_packing_slip'),      name='print_packing_slip'),
    path('print/payment-receipt/<int:pk>/',
         lazy_view('lumra_config.print_app.views.print_payment_receipt'),   name='print_payment_receipt'),
    path('print/receipt/<int:pk>/',
         lazy_view('lumra_config.print_app.views.print_receipt'),           name='print_receipt'),
    path('print/production-order/<int:pk>/',
         lazy_view('lumra_config.print_app.views.print_production_order'),  name='print_production_order'),
    path('print/credit-note/<int:pk>/',
         lazy_view('lumra_config.print_app.views.print_credit_note'),       name='print_credit_note'),
    path('print/stock-opname/<int:pk>/',
         lazy_view('lumra_config.print_app.views.print_stock_opname'),      name='print_stock_opname'),

    # ----- Returns & Refunds -------------------------------------------------
    path('sales/retur/',
         lazy_view('lumra_config.sales.views.retur_list'),                  name='retur_list'),
    path('sales/retur/add/',
         lazy_view('lumra_config.sales.views.retur_form'),                  name='retur_form'),
    path('sales/retur/<int:pk>/',
         lazy_view('lumra_config.sales.views.retur_detail'),                name='retur_detail'),
    path('sales/retur/<int:pk>/edit/',
         lazy_view('lumra_config.sales.views.retur_form'),                  name='retur_edit'),
    
    # ----- Sales History & Analytics -----------------------------------------
    path('sales/history/',
         lazy_view('lumra_config.sales.views.sales_history_view'),          name='sales_history'),
    path('sales/history/products/',
         lazy_view('lumra_config.sales.views.sales_history_products_view'), name='sales_history_products'),
    path('sales/performance/',
         lazy_view('lumra_config.sales.views.sales_performance_view'),      name='sales_performance'),

    # =========================================================================
    # PURCHASING
    # =========================================================================
    path('purchasing/',
         lazy_view('lumra_config.sales.views.purchasing_view'),             name='purchasing'),

    # =========================================================================
    # MARKETING & PROMOTIONS  — Campaigns · Discounts · Loyalty
    # =========================================================================

    # ----- Campaigns ---------------------------------------------------------
    path('marketing/campaigns/',
         lazy_view('lumra_config.marketing.views.campaign_list_view'),          name='campaign_list'),
    path('marketing/campaigns/add/',
         lazy_view('lumra_config.marketing.views.add_campaign_view'),           name='add_campaign'),
    path('marketing/campaigns/<int:campaign_id>/edit/',
         lazy_view('lumra_config.marketing.views.edit_campaign_view'),          name='edit_campaign'),
    path('marketing/campaigns/<int:campaign_id>/delete/',
         lazy_view('lumra_config.marketing.views.delete_campaign_view'),        name='delete_campaign'),
    # Legacy paths (old sidebar links still using /campaigns/)
    path('campaigns/',
         RedirectView.as_view(url='/marketing/campaigns/', permanent=False)),
    path('campaigns/add/',
         RedirectView.as_view(url='/marketing/campaigns/add/', permanent=False)),

    # ----- Discounts ---------------------------------------------------------
    path('marketing/discounts/',
         lazy_view('lumra_config.marketing.views.discount_list_view'),          name='discount_list'),
    path('marketing/discounts/add/',
         lazy_view('lumra_config.marketing.views.add_discount_view'),           name='add_discount'),
    path('marketing/discounts/<int:discount_id>/edit/',
         lazy_view('lumra_config.marketing.views.edit_discount_view'),          name='edit_discount'),
    path('marketing/discounts/<int:discount_id>/delete/',
         lazy_view('lumra_config.marketing.views.delete_discount_view'),        name='delete_discount'),
    # Legacy paths
    path('discounts/',
         RedirectView.as_view(url='/marketing/discounts/', permanent=False)),
    path('discounts/add/',
         RedirectView.as_view(url='/marketing/discounts/add/', permanent=False)),

    # ----- Loyalty Program ---------------------------------------------------
    path('marketing/loyalty/',
         lazy_view('lumra_config.marketing.views.loyalty_members_view'),        name='loyalty_members'),
    path('marketing/loyalty/add/',
         lazy_view('lumra_config.marketing.views.add_loyalty_member_view'),     name='add_loyalty_member'),
    path('marketing/loyalty/<int:member_id>/edit/',
         lazy_view('lumra_config.marketing.views.edit_loyalty_member_view'),    name='edit_loyalty_member'),
    path('marketing/loyalty/<int:member_id>/delete/',
         lazy_view('lumra_config.marketing.views.delete_loyalty_member_view'),  name='delete_loyalty_member'),
    # Legacy paths
    path('loyalty/',
         RedirectView.as_view(url='/marketing/loyalty/', permanent=False)),
    path('loyalty/add/',
         RedirectView.as_view(url='/marketing/loyalty/add/', permanent=False)),

    # ----- Vouchers ----------------------------------------------------------
    path('marketing/vouchers/',
         lazy_view('lumra_config.marketing.views.voucher_list'),                  name='voucher_list'),
    path('marketing/vouchers/add/',
         lazy_view('lumra_config.marketing.views.voucher_form'),                  name='voucher_form'),
    path('marketing/vouchers/<int:pk>/edit/',
         lazy_view('lumra_config.marketing.views.voucher_form'),                  name='voucher_edit'),
    path('marketing/voucher-claims/',
         lazy_view('lumra_config.marketing.views.voucher_claim_log'),             name='voucher_claim_log'),

    # ----- Customer Segments -------------------------------------------------
    path('marketing/segments/',
         lazy_view('lumra_config.marketing.views.customer_segment_list'),         name='customer_segment_list'),
    path('marketing/segments/add/',
         lazy_view('lumra_config.marketing.views.customer_segment_form'),         name='customer_segment_form'),
    path('marketing/segments/<int:pk>/edit/',
         lazy_view('lumra_config.marketing.views.customer_segment_form'),         name='customer_segment_edit'),

    # ----- Promotions --------------------------------------------------------
    path('marketing/promotions/',
         lazy_view('lumra_config.marketing.views.promotion_calendar'),            name='promotion_calendar'),

    # =========================================================================
    # INSIGHTS & REPORTS
    # =========================================================================

    # ----- Insights (high-level analytics) -----------------------------------
    path('insights/sales_insight/',
         lazy_view('lumra_config.sales.views.sales_insight_view'),          name='sales_insight'),
    path('insights/financial/',
         lazy_view('lumra_config.reports.views.financial_reports_view'),      name='financial_reports'),
    path('insights/market/',
         lazy_view('lumra_config.reports.views.market_insights_view'),        name='market_insights'),
    path('insights/trends/',
         lazy_view('lumra_config.reports.views.trends_analysis_view'),        name='trends_analysis'),
    path('insights/activity/',
         lazy_view('lumra_config.reports.views.activity_log_view'),           name='activity_log'),
    path('insights/download-report/<str:report_type>/',
         lazy_view('lumra_config.reports.views.download_report_view'),        name='download_report'),
    path('insights/export-trends/<str:trend_type>/',
         lazy_view('lumra_config.reports.views.export_trends_view'),          name='export_trends'),

    # ----- Operational Reports -----------------------------------------------
    path('reports/sales/',
         lazy_view('lumra_config.reports.views.sales_report'),                name='sales_report'),
    path('reports/transactions/',
         lazy_view('lumra_config.reports.views.transaction_summary'),         name='transaction_summary'),
    path('reports/transfers/',
         lazy_view('lumra_config.reports.views.transfer_report'),             name='transfer_report'),
    path('reports/requisitions/',
         lazy_view('lumra_config.reports.views.requisition_report'),          name='requisition_report'),
    path('reports/purchasing/',
         lazy_view('lumra_config.sales.views.purchasing_report'),           name='purchasing_report'),
    path('reports/inventory-log/',
         lazy_view('lumra_config.reports.views.report_inventory_log'),        name='report_inventory_log'),
    path('reports/inventory-low/',
         lazy_view('lumra_config.reports.views.report_inventory_low'),        name='report_inventory_low'),
    path('reports/inventory-stock/',
         lazy_view('lumra_config.reports.views.report_inventory_stock'),      name='report_inventory_stock'),
    path('reports/profit-loss-detail/',
         lazy_view('lumra_config.reports.views.report_profit_loss_detail'),   name='report_profit_loss_detail'),
    path('reports/sales-by-outlet/',
         lazy_view('lumra_config.reports.views.report_sales_by_outlet'),      name='report_sales_by_outlet'),
    path('reports/sales-by-payment/',
         lazy_view('lumra_config.reports.views.report_sales_by_payment'),     name='report_sales_by_payment'),
    path('reports/sales-by-product/',
         lazy_view('lumra_config.master_data.views.report_sales_by_product'),     name='report_sales_by_product'),
    path('reports/sales-summary/',
         lazy_view('lumra_config.reports.views.report_sales_summary'),        name='report_sales_summary'),

    # =========================================================================
    # USERS
    # =========================================================================
    path('users/', lazy_view('lumra_config.settings_app.views.users_view'),        name='users'),

    # =========================================================================
    # PROFILE & SETTINGS
    # =========================================================================
    path('profile/',
         lazy_view('lumra_config.settings_app.views.profile_view'),                name='profile'),
    path('settings/',
         lazy_view('lumra_config.settings_app.views.settings_view'),               name='settings'),
    path('settings/system/',
         lazy_view('lumra_config.settings_app.views.system_status'),               name='system_status'),
    path('settings/business/',
         lazy_view('lumra_config.settings_app.views.business_settings_view'),      name='business_settings'),
    path('settings/business-profile/',
         lazy_view('lumra_config.settings_app.views.business_profile'),            name='business_profile'),
    path('settings/business/general/',
         lazy_view('lumra_config.settings_app.views.business_form_general_view'),  name='business_form_general'),
    path('settings/business/feature-matrix/',
         lazy_view('lumra_config.settings_app.views.business_feature_matrix_view'),name='business_feature_matrix'),
    path('settings/business/roles/',
         lazy_view('lumra_config.settings_app.views.user_roles_permissions_view'), name='user_roles_permissions'),

    # =========================================================================
    # ACCOUNTING — Chart of Accounts · Ledger · Journals · Reports
    # =========================================================================
    path('accounting/coa/',
         lazy_view('lumra_config.accounting.views.chart_of_accounts'),            name='chart_of_accounts'),
    path('accounting/coa/add/',
         lazy_view('lumra_config.accounting.views.chart_of_accounts_form'),       name='chart_of_accounts_form'),
    path('accounting/coa/<int:pk>/edit/',
         lazy_view('lumra_config.accounting.views.chart_of_accounts_form'),       name='chart_of_accounts_edit'),
    path('accounting/ledger/',
         lazy_view('lumra_config.accounting.views.general_ledger'),               name='general_ledger'),
    path('accounting/journal/',
         lazy_view('lumra_config.accounting.views.journal_entry_list'),           name='journal_entry_list'),
    path('accounting/journal/add/',
         lazy_view('lumra_config.accounting.views.journal_entry_form'),           name='journal_entry_form'),
    path('accounting/journal/<int:pk>/',
         lazy_view('lumra_config.accounting.views.journal_entry_detail'),         name='journal_entry_detail'),
    path('accounting/voucher/',
         lazy_view('lumra_config.accounting.views.payment_voucher_form'),         name='payment_voucher_form'),
    path('accounting/trial-balance/',
         lazy_view('lumra_config.accounting.views.trial_balance'),                name='trial_balance'),
    path('accounting/balance-sheet/',
         lazy_view('lumra_config.accounting.views.balance_sheet'),                name='balance_sheet'),
    path('accounting/income-statement/',
         lazy_view('lumra_config.accounting.views.profit_loss_statement'),        name='profit_loss_statement'),
    path('accounting/cash-flow/',
         lazy_view('lumra_config.accounting.views.cash_flow_statement'),          name='cash_flow_statement'),
    path('accounting/ar/',
         lazy_view('lumra_config.accounting.views.accounts_receivable'),          name='accounts_receivable'),
    path('accounting/ap/',
         lazy_view('lumra_config.accounting.views.accounts_payable'),             name='accounts_payable'),

    # =========================================================================
    # MESSAGES — Inbox · Compose · Broadcast · Templates
    # =========================================================================
    path('messages/inbox/',
         lazy_view('lumra_config.messages.views.inbox'),                          name='inbox'),
    path('messages/inbox/<int:pk>/',
         lazy_view('lumra_config.messages.views.message_detail'),                 name='message_detail'),
    path('messages/compose/',
         lazy_view('lumra_config.messages.views.compose_message'),                name='compose_message'),
    path('messages/broadcast/',
         lazy_view('lumra_config.messages.views.broadcast_message'),              name='broadcast_message'),
    path('messages/templates/',
         lazy_view('lumra_config.messages.views.message_templates'),              name='message_templates'),
    path('messages/notification/',
         lazy_view('lumra_config.messages.views.notification_center'),            name='notification_center'),

    # =========================================================================
    # EXTENDED SETTINGS & ADMIN
    # =========================================================================
    path('settings/users/',
         lazy_view('lumra_config.settings_app.views.users_list'),                 name='users_list'),
    path('settings/users/add/',
         lazy_view('lumra_config.settings_app.views.user_form'),                  name='user_form'),
    path('settings/permissions/',
         lazy_view('lumra_config.settings_app.views.permission_matrix'),          name='permission_matrix'),
    path('settings/email/',
         lazy_view('lumra_config.settings_app.views.email_settings'),             name='email_settings'),
    path('settings/notifications/',
         lazy_view('lumra_config.settings_app.views.notification_settings'),      name='notification_settings'),
    path('settings/numbering/',
         lazy_view('lumra_config.settings_app.views.numbering_settings'),         name='numbering_settings'),
    path('settings/backup/',
         lazy_view('lumra_config.settings_app.views.backup_restore'),             name='backup_restore'),
    path('settings/api-keys/',
         lazy_view('lumra_config.settings_app.views.api_keys'),                   name='api_keys'),

    # =========================================================================
    # MASTER DATA EXTENDED — Bank Accounts · Payment Terms · Taxes · Reason Codes
    # =========================================================================
    path('bank-accounts/',
         lazy_view('lumra_config.master_data.views.bank_accounts'),               name='bank_accounts'),
    path('bank-accounts/add/',
         lazy_view('lumra_config.master_data.views.bank_account_form'),           name='bank_account_form'),
    path('bank-accounts/<int:pk>/edit/',
         lazy_view('lumra_config.master_data.views.bank_account_form'),           name='bank_account_edit'),
    path('payment-terms/',
         lazy_view('lumra_config.master_data.views.payment_terms_list'),          name='payment_terms_list'),
    path('payment-terms/add/',
         lazy_view('lumra_config.master_data.views.payment_terms_form'),          name='payment_terms_form'),
    path('payment-terms/<int:pk>/edit/',
         lazy_view('lumra_config.master_data.views.payment_terms_form'),          name='payment_terms_edit'),
    path('taxes/',
         lazy_view('lumra_config.master_data.views.tax_list'),                    name='tax_list'),
    path('taxes/add/',
         lazy_view('lumra_config.master_data.views.tax_form'),                    name='tax_form'),
    path('taxes/<int:pk>/edit/',
         lazy_view('lumra_config.master_data.views.tax_form'),                    name='tax_edit'),
    path('reason-codes/',
         lazy_view('lumra_config.master_data.views.reason_codes'),                name='reason_codes'),
    path('tags/',
         lazy_view('lumra_config.master_data.views.tags_list'),                   name='tags_list'),
    path('tags/add/',
         lazy_view('lumra_config.master_data.views.tags_form'),                   name='tags_form'),
    path('tags/<int:pk>/edit/',
         lazy_view('lumra_config.master_data.views.tags_form'),                   name='tags_edit'),

    # =========================================================================
    # PRODUCTION — BOM · Production Orders · Scheduling · Costing
    # =========================================================================
    path('production/bom/',
         lazy_view('lumra_config.production.views.bom_list'),                     name='bom_list'),
    path('production/bom/add/',
         lazy_view('lumra_config.production.views.bom_form'),                     name='bom_form'),
    path('production/bom/<int:pk>/',
         lazy_view('lumra_config.production.views.bom_detail'),                   name='bom_detail'),
    path('production/bom/<int:pk>/edit/',
         lazy_view('lumra_config.production.views.bom_form'),                     name='bom_edit'),
    path('production/order/',
         lazy_view('lumra_config.production.views.production_order_list'),        name='production_order_list'),
    path('production/order/add/',
         lazy_view('lumra_config.production.views.production_order_form'),        name='production_order_form'),
    path('production/order/<int:pk>/',
         lazy_view('lumra_config.production.views.production_order_detail'),      name='production_order_detail'),
    path('production/order/<int:pk>/edit/',
         lazy_view('lumra_config.production.views.production_order_form'),        name='production_order_edit'),
    path('production/scheduling/',
         lazy_view('lumra_config.production.views.production_scheduling'),        name='production_scheduling'),
    path('production/consumption/',
         lazy_view('lumra_config.production.views.material_consumption'),         name='material_consumption'),
    path('production/finished/',
         lazy_view('lumra_config.production.views.finished_goods_receipt'),       name='finished_goods_receipt'),
    path('production/costing/',
         lazy_view('lumra_config.production.views.production_costing'),           name='production_costing'),
    path('production/waste/',
         lazy_view('lumra_config.production.views.production_waste'),             name='production_waste'),

    # =========================================================================
    # REPORTS — Expiry · Inventory Age · Customer LTV · Production · Staff
    # =========================================================================
    path('reports/expiry/',
         lazy_view('lumra_config.reports.views.report_expiry'),                   name='report_expiry'),
    path('reports/inventory-age/',
         lazy_view('lumra_config.reports.views.report_inventory_age'),            name='report_inventory_age'),
    path('reports/customer-lifetime/',
         lazy_view('lumra_config.reports.views.report_customer_lifetime'),        name='report_customer_lifetime'),
    path('reports/production/',
         lazy_view('lumra_config.reports.views.report_production'),               name='report_production'),
    path('reports/staff/',
         lazy_view('lumra_config.reports.views.report_staff_performance'),        name='report_staff_performance'),
    path('reports/sales/',
         lazy_view('lumra_config.reports.views.sales_report'),                    name='sales_report'),

    # =========================================================================
    # PAGES & UTILITIES
    # =========================================================================
    path('about/',   lazy_view('lumra_config.settings_app.views.about_view'),      name='about'),
    path('contact/', lazy_view('lumra_config.settings_app.views.contact_view'),    name='contact'),
    path('pricing/', lazy_view('lumra_config.settings_app.views.pricing_view'),    name='pricing'),
    path('search/',  lazy_view('lumra_config.settings_app.views.search_view'),     name='search'),

    # =========================================================================
    # AUTHENTICATION
    # =========================================================================
    path('auth/login/',  lazy_view('lumra_config.auth_app.views.login_view'),  name='login'),
    path('auth/logout/', lazy_view('lumra_config.auth_app.views.logout_view'), name='logout'),

    # =========================================================================
    # INTERNAL API ENDPOINTS
    # =========================================================================
    path('api/dashboard/data/',
         lazy_view('lumra_config.views.dashboard_views.api_dashboard_data'),          name='api_dashboard_data'),
    path('api/dashboard/chart-data/',
         lazy_view('lumra_config.views.dashboard_views.api_dashboard_chart_data'),    name='api_dashboard_chart_data'),
    path('api/requisition/submit/',
         lazy_view('lumra_config.api.views.submit_requisition'),          name='submit_requisition'),
    path('api/requisition/<int:requisition_id>/approve/',
         lazy_view('lumra_config.inventory.views.approve_requisition'),         name='approve_requisition'),
    path('api/transfer/<int:transfer_id>/confirm/',
         lazy_view('lumra_config.api.views.confirm_receipt'),             name='confirm_receipt'),
    path('api/submit-stock-allocation/',
         lazy_view('lumra_config.inventory.views.submit_stock_allocation'),     name='submit_stock_allocation'),
    path('api/purchases/submit/',
         lazy_view('lumra_config.api.views.submit_purchases'),  name='submit_purchases'),
    path('api/location-stock/<str:product_sku>/',
         lazy_view('lumra_config.api.views.get_location_stock'),          name='get_location_stock'),
    # bulk-import endpoint used by products page
    path('api/products/create/',
         lazy_view('lumra_config.inventory.views.product_create_api'),
         name='product_create_api'),
    path('api/products/<int:product_id>/update/',
         lazy_view('lumra_config.inventory.views.product_update_api'),
         name='product_update_api'),
    path('api/products/<int:product_id>/delete/',
         lazy_view('lumra_config.inventory.views.product_delete_api'),
         name='product_delete_api'),
    path('api/products/bulk/',
         lazy_view('lumra_config.inventory.views.product_bulk_api'),
         name='product_bulk_api'),
    path('api/products/variants/<int:variant_id>/update/',
         lazy_view('lumra_config.inventory.views.variant_update_api'),
         name='variant_update_api'),
    path('api/products/import/',
         lazy_view('lumra_config.inventory.views.products_import'),
         name='products_import'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls", namespace="django_browser_reload")),
    ]
