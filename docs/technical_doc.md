# 📖 Lumra ERP — Buku Dokumentasi Teknis

> Dibuat otomatis dari source code pada 23 March 2026 07:31

---

## 📋 Daftar Isi

1. [Arsitektur Project](#arsitektur-project)
2. [Database & Model](#database-model)
3. [URL → View → Template](#url-view-template)
4. [Settings & Konfigurasi](#settings-konfigurasi)
5. [Template Audit](#template-audit)

---

## 1. Arsitektur Project

```
lumra/
├───.lumra_dup_backup/
│   └───20260313_111105/
│       └───lumra_pages/
│           ├───inventory/
│           ├───master_data/
│           └───sales/
├───.lumra_fix_all_backup/
│   ├───20260312_143957/
│   │   └───lumra_config/
│   │       └───views/
│   └───20260313_141537/
│       └───lumra_config/
│           └───views/
├───.lumra_master_backup/
│   ├───20260313_140431/
│   │   └───lumra_config/
│   │       └───templates/
│   └───20260313_142714/
│       └───lumra_config/
│           └───views/
├───.lumra_recolor_backup/
│   ├───20260314_095002/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260314_095003/
│   │   └───lumra_config/
│   │       └───templates/
│   └───20260314_095004/
│       └───lumra_config/
│           └───templates/
├───.lumra_rename_backup/
│   └───20260313_125839/
│       └───lumra_config/
│           └───templates/
├───.lumra_reorg_backup/
│   └───20260313_111548/
│       └───views/
│           ├───misc_views.py
│           └───stock_movement_views.py
├───.lumra_sync_backup/
│   └───20260310_150537/
├───.lumra_theme_backup/
│   └───20260314_091049/
│       └───lumra_config/
│           └───templates/
├───_archive/
│   └───lumra_pages_root/
│       └───20260312_143030/
│           ├───about.html
│           ├───activity_log.html
│           ├───add_stock_movement.html
│           ├───campaign.html
│           ├───contact.html
│           ├───customers.html
│           ├───dashboard.html
│           ├───discount.html
│           ├───loyalty_members.html
│           ├───market_insights.html
│           ├───notification.html
│           ├───profile.html
│           ├───search.html
│           ├───stock_movement.html
│           ├───trends_analysis.html
│           ├───user_roles_permissions.html
│           └───users.html
├───_emerald_upgrade_backup/
│   └───20260314_131938/
│       ├───base/
│       │   ├───activity_drawer.html
│       │   ├───approval_modal.html
│       │   ├───base.html
│       │   ├───navbar.html
│       │   ├───sidebar.html
│       │   └───sidebar_right.html
│       └───lumra_pages/
│           ├───auth/
│           ├───inventory/
│           ├───marketing/
│           ├───master_data/
│           ├───messages/
│           ├───reports/
│           ├───sales_insight/
│           └───settings/
├───_full_migrator_backup/
│   ├───20260318_085959/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_090000/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_090001/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_090002/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_090003/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_090004/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_090005/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_090856/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_090909/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_090910/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_090911/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_090912/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_091738/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_091739/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_091740/
│   │   └───lumra_config/
│   │       └───templates/
│   ├───20260318_091741/
│   │   └───lumra_config/
│   │       └───templates/
│   └───20260318_091742/
│       └───lumra_config/
│           └───templates/
├───_glass_backup_20260318_201403/
│   ├───about.html
│   ├───activity_drawer.html
│   ├───activity_log.html
│   ├───add_campaign.html
│   ├───add_stock_movement.html
│   ├───approval_modal.html
│   ├───base_report.html
│   ├───business_feature_matrix.html
│   ├───business_form_general.html
│   ├───business_profile.html
│   ├───business_settings.html
│   ├───campaign.html
│   ├───campaign_list.html
│   ├───categories_list.html
│   ├───category_form.html
│   ├───contact.html
│   ├───customer.html
│   ├───customer_detail.html
│   ├───customer_form.html
│   ├───customers.html
│   ├───customers_list.html
│   ├───discount.html
│   ├───error_403.html
│   ├───financial_reports.html
│   ├───location_list.html
│   ├───locations.html
│   ├───login.html
│   ├───loyalty_members.html
│   ├───market_insights.html
│   ├───navbar.html
│   ├───notification.html
│   ├───pos.html
│   ├───product_details.html
│   ├───product_list.html
│   ├───products.html
│   ├───profile.html
│   ├───purchasing_report.html
│   ├───recipe_detail.html
│   ├───recipe_form.html
│   ├───recipe_list.html
│   ├───register.html
│   ├───report_activity_log.html
│   ├───report_inventory_log.html
│   ├───report_inventory_low.html
│   ├───report_inventory_stock.html
│   ├───report_profit_loss_detail.html
│   ├───report_sales_by_outlet.html
│   ├───report_sales_by_payment.html
│   ├───report_sales_by_product.html
│   ├───report_sales_summary.html
│   ├───reporting.html
│   ├───requisition_report.html
│   ├───sales_history.html
│   ├───sales_history_product.html
│   ├───sales_intelligence.html
│   ├───sales_performance.html
│   ├───sales_report.html
│   ├───sales_report_after.html
│   ├───search.html
│   ├───settings.html
│   ├───sidebar.html
│   ├───sidebar1.html
│   ├───sidebar_right.html
│   ├───stock_movement.html
│   ├───stock_movement_form.html
│   ├───stock_opname.html
│   ├───stock_opname_approval_detail.html
│   ├───stock_opname_approvals.html
│   ├───stock_opname_form.html
│   ├───stock_opname_locations.html
│   ├───stock_opname_session_detail.html
│   ├───stock_overview.html
│   ├───stock_planning.html
│   ├───stock_purchasing.html
│   ├───supplier_price_confirm_delete.html
│   ├───supplier_price_form.html
│   ├───supplier_price_list.html
│   ├───system_status.html
│   ├───transaction_summary.html
│   ├───transfer_report.html
│   ├───trends_analysis.html
│   ├───unit_form.html
│   ├───units_list.html
│   ├───user_list.html
│   ├───user_roles_permissions.html
│   ├───users.html
│   ├───vendor_form.html
│   ├───vendor_list.html
│   └───vendors_list.html
├───_strip_backup_20260318_221043/
│   ├───about.html
│   ├───about_20260316_104852.html
│   ├───about_221045.html
│   ├───about_221046.html
│   ├───about_221047.html
│   ├───about_221050.html
│   ├───add_campaign.html
│   ├───add_campaign_20260316_104850.html
│   ├───add_campaign_20260316_123608.html
│   ├───add_campaign_221044.html
│   ├───add_campaign_221045.html
│   ├───add_campaign_221046.html
│   ├───add_campaign_221047.html
│   ├───add_campaign_221049.html
│   ├───add_stock_movement.html
│   ├───add_stock_movement_20260316_104849.html
│   ├───add_stock_movement_221043.html
│   ├───add_stock_movement_221044.html
│   ├───add_stock_movement_221045.html
│   ├───add_stock_movement_221046.html
│   ├───add_stock_movement_221047.html
│   ├───add_stock_movement_221049.html
│   ├───base.html
│   ├───base_20260316_104849.html
│   ├───base_221044.html
│   ├───base_221046.html
│   ├───base_221048.html
│   ├───base_221049.html
│   ├───base_221050.html
│   ├───business_feature_matrix.html
│   ├───business_feature_matrix_20260316_104852.html
│   ├───business_feature_matrix_20260316_123608.html
│   ├───business_feature_matrix_221045.html
│   ├───business_feature_matrix_221047.html
│   ├───business_feature_matrix_221050.html
│   ├───business_form_general.html
│   ├───business_form_general_20260316_104852.html
│   ├───business_form_general_20260316_123608.html
│   ├───business_form_general_221044.html
│   ├───business_form_general_221045.html
│   ├───business_form_general_221047.html
│   ├───business_form_general_221050.html
│   ├───business_profile.html
│   ├───business_profile_20260316_104852.html
│   ├───business_profile_20260316_123608.html
│   ├───business_profile_221045.html
│   ├───business_profile_221047.html
│   ├───business_profile_221050.html
│   ├───business_settings.html
│   ├───business_settings_20260316_104852.html
│   ├───business_settings_20260316_123608.html
│   ├───business_settings_221045.html
│   ├───business_settings_221046.html
│   ├───business_settings_221047.html
│   ├───business_settings_221050.html
│   ├───campaign.html
│   ├───campaign_20260316_104850.html
│   ├───campaign_20260316_123608.html
│   ├───campaign_221044.html
│   ├───campaign_221045.html
│   ├───campaign_221046.html
│   ├───campaign_221047.html
│   ├───campaign_221049.html
│   ├───campaign_list.html
│   ├───campaign_list_20260316_104850.html
│   ├───campaign_list_20260316_123608.html
│   ├───campaign_list_221044.html
│   ├───campaign_list_221045.html
│   ├───campaign_list_221046.html
│   ├───campaign_list_221047.html
│   ├───campaign_list_221049.html
│   ├───categories_list.html
│   ├───categories_list_20260316_104850.html
│   ├───categories_list_20260316_123608.html
│   ├───categories_list_221044.html
│   ├───categories_list_221045.html
│   ├───categories_list_221046.html
│   ├───categories_list_221047.html
│   ├───categories_list_221050.html
│   ├───category_form.html
│   ├───category_form_20260316_104850.html
│   ├───category_form_221044.html
│   ├───category_form_221046.html
│   ├───category_form_221047.html
│   ├───category_form_221050.html
│   ├───customer_detail.html
│   ├───customer_detail_20260316_104850.html
│   ├───customer_detail_20260316_123608.html
│   ├───customer_detail_221044.html
│   ├───customer_detail_221046.html
│   ├───customer_detail_221047.html
│   ├───customer_detail_221050.html
│   ├───customer_form.html
│   ├───customer_form_20260316_104850.html
│   ├───customer_form_20260316_123608.html
│   ├───customer_form_221044.html
│   ├───customer_form_221045.html
│   ├───customer_form_221046.html
│   ├───customer_form_221047.html
│   ├───customer_form_221050.html
│   ├───customers.html
│   ├───customers_20260316_104850.html
│   ├───customers_20260316_123608.html
│   ├───customers_221044.html
│   ├───customers_221045.html
│   ├───customers_221046.html
│   ├───customers_221047.html
│   ├───customers_221050.html
│   ├───customers_list.html
│   ├───customers_list_20260316_104850.html
│   ├───customers_list_20260316_123608.html
│   ├───customers_list_221044.html
│   ├───customers_list_221045.html
│   ├───customers_list_221046.html
│   ├───customers_list_221047.html
│   ├───customers_list_221050.html
│   ├───dashboard.html
│   ├───dashboard_20260316_104852.html
│   ├───dashboard_20260316_123608.html
│   ├───dashboard_221046.html
│   ├───dashboard_221050.html
│   ├───financial_reports.html
│   ├───financial_reports_20260316_104852.html
│   ├───financial_reports_20260316_123608.html
│   ├───financial_reports_221046.html
│   ├───financial_reports_221047.html
│   ├───financial_reports_221050.html
│   ├───inventory.html
│   ├───location_list.html
│   ├───location_list_20260316_104850.html
│   ├───location_list_20260316_123608.html
│   ├───location_list_221044.html
│   ├───location_list_221045.html
│   ├───location_list_221046.html
│   ├───location_list_221047.html
│   ├───location_list_221050.html
│   ├───locations.html
│   ├───locations_20260316_104850.html
│   ├───locations_20260316_123608.html
│   ├───locations_221044.html
│   ├───locations_221045.html
│   ├───locations_221046.html
│   ├───locations_221047.html
│   ├───locations_221050.html
│   ├───market_insights.html
│   ├───market_insights_20260316_104852.html
│   ├───market_insights_20260316_123608.html
│   ├───market_insights_221045.html
│   ├───market_insights_221046.html
│   ├───market_insights_221047.html
│   ├───market_insights_221050.html
│   ├───notification.html
│   ├───notification_20260316_104851.html
│   ├───notification_20260316_123608.html
│   ├───notification_221046.html
│   ├───notification_221047.html
│   ├───notification_221050.html
│   ├───pos.html
│   ├───pos_20260316_104852.html
│   ├───pos_20260316_123608.html
│   ├───pos_221045.html
│   ├───pos_221047.html
│   ├───pos_221050.html
│   ├───product_details.html
│   ├───product_details_20260316_104849.html
│   ├───product_details_20260316_123608.html
│   ├───product_details_221043.html
│   ├───product_details_221044.html
│   ├───product_details_221045.html
│   ├───product_details_221046.html
│   ├───product_details_221047.html
│   ├───product_details_221049.html
│   ├───product_list.html
│   ├───product_list_20260316_104849.html
│   ├───product_list_20260316_123608.html
│   ├───product_list_221044.html
│   ├───product_list_221045.html
│   ├───product_list_221046.html
│   ├───product_list_221047.html
│   ├───product_list_221049.html
│   ├───products.html
│   ├───products_20260316_104849.html
│   ├───products_20260316_123608.html
│   ├───products_221043.html
│   ├───products_221044.html
│   ├───products_221045.html
│   ├───products_221046.html
│   ├───products_221047.html
│   ├───products_221049.html
│   ├───profile.html
│   ├───profile_20260316_104852.html
│   ├───profile_20260316_123608.html
│   ├───profile_221045.html
│   ├───profile_221046.html
│   ├───profile_221047.html
│   ├───profile_221050.html
│   ├───purchasing_report.html
│   ├───purchasing_report_20260316_104851.html
│   ├───purchasing_report_20260316_123608.html
│   ├───purchasing_report_221045.html
│   ├───purchasing_report_221046.html
│   ├───purchasing_report_221047.html
│   ├───purchasing_report_221048.html
│   ├───purchasing_report_221050.html
│   ├───report_inventory_log.html
│   ├───report_inventory_log_20260316_104851.html
│   ├───report_inventory_log_20260316_123608.html
│   ├───report_inventory_log_221043.html
│   ├───report_inventory_log_221044.html
│   ├───report_inventory_log_221045.html
│   ├───report_inventory_log_221046.html
│   ├───report_inventory_log_221047.html
│   ├───report_inventory_log_221050.html
│   ├───report_inventory_low.html
│   ├───report_inventory_low_20260316_104851.html
│   ├───report_inventory_low_20260316_123608.html
│   ├───report_inventory_low_221043.html
│   ├───report_inventory_low_221044.html
│   ├───report_inventory_low_221045.html
│   ├───report_inventory_low_221046.html
│   ├───report_inventory_low_221047.html
│   ├───report_inventory_low_221050.html
│   ├───report_inventory_stock.html
│   ├───report_inventory_stock_20260316_104851.html
│   ├───report_inventory_stock_20260316_123608.html
│   ├───report_inventory_stock_221043.html
│   ├───report_inventory_stock_221044.html
│   ├───report_inventory_stock_221045.html
│   ├───report_inventory_stock_221046.html
│   ├───report_inventory_stock_221047.html
│   ├───report_inventory_stock_221050.html
│   ├───report_profit_loss_detail.html
│   ├───report_profit_loss_detail_20260316_104851.html
│   ├───report_profit_loss_detail_20260316_123608.html
│   ├───report_profit_loss_detail_221044.html
│   ├───report_profit_loss_detail_221045.html
│   ├───report_profit_loss_detail_221046.html
│   ├───report_profit_loss_detail_221047.html
│   ├───report_profit_loss_detail_221050.html
│   ├───report_sales_by_outlet.html
│   ├───report_sales_by_outlet_20260316_104851.html
│   ├───report_sales_by_outlet_20260316_123608.html
│   ├───report_sales_by_outlet_221044.html
│   ├───report_sales_by_outlet_221045.html
│   ├───report_sales_by_outlet_221046.html
│   ├───report_sales_by_outlet_221047.html
│   ├───report_sales_by_outlet_221050.html
│   ├───report_sales_by_payment.html
│   ├───report_sales_by_payment_20260316_104851.html
│   ├───report_sales_by_payment_20260316_123608.html
│   ├───report_sales_by_payment_221044.html
│   ├───report_sales_by_payment_221045.html
│   ├───report_sales_by_payment_221046.html
│   ├───report_sales_by_payment_221047.html
│   ├───report_sales_by_payment_221050.html
│   ├───report_sales_by_product.html
│   ├───report_sales_by_product_20260316_104851.html
│   ├───report_sales_by_product_20260316_123608.html
│   ├───report_sales_by_product_221043.html
│   ├───report_sales_by_product_221044.html
│   ├───report_sales_by_product_221045.html
│   ├───report_sales_by_product_221046.html
│   ├───report_sales_by_product_221047.html
│   ├───report_sales_by_product_221050.html
│   ├───report_sales_summary.html
│   ├───report_sales_summary_20260316_104851.html
│   ├───report_sales_summary_20260316_123608.html
│   ├───report_sales_summary_221044.html
│   ├───report_sales_summary_221045.html
│   ├───report_sales_summary_221046.html
│   ├───report_sales_summary_221047.html
│   ├───report_sales_summary_221050.html
│   ├───requisition_report.html
│   ├───requisition_report_20260316_104852.html
│   ├───requisition_report_20260316_123608.html
│   ├───requisition_report_221044.html
│   ├───requisition_report_221045.html
│   ├───requisition_report_221046.html
│   ├───requisition_report_221047.html
│   ├───requisition_report_221050.html
│   ├───sales_history.html
│   ├───sales_history_20260316_104852.html
│   ├───sales_history_20260316_123608.html
│   ├───sales_history_221044.html
│   ├───sales_history_221045.html
│   ├───sales_history_221046.html
│   ├───sales_history_221047.html
│   ├───sales_history_221050.html
│   ├───sales_history_product.html
│   ├───sales_history_product_20260316_104852.html
│   ├───sales_history_product_20260316_123608.html
│   ├───sales_history_product_221043.html
│   ├───sales_history_product_221044.html
│   ├───sales_history_product_221046.html
│   ├───sales_history_product_221047.html
│   ├───sales_history_product_221050.html
│   ├───sales_insight.html
│   ├───sales_intelligence.html
│   ├───sales_intelligence_20260316_104852.html
│   ├───sales_intelligence_20260316_123608.html
│   ├───sales_intelligence_221045.html
│   ├───sales_intelligence_221047.html
│   ├───sales_intelligence_221050.html
│   ├───sales_performance.html
│   ├───sales_performance_20260316_104852.html
│   ├───sales_performance_20260316_123608.html
│   ├───sales_performance_221044.html
│   ├───sales_performance_221047.html
│   ├───sales_performance_221050.html
│   ├───sales_report.html
│   ├───sales_report_20260316_104852.html
│   ├───sales_report_20260316_123608.html
│   ├───sales_report_221044.html
│   ├───sales_report_221046.html
│   ├───sales_report_221047.html
│   ├───sales_report_221050.html
│   ├───sidebar_right.html
│   ├───sidebar_right_20260316_104849.html
│   ├───sidebar_right_20260316_123607.html
│   ├───sidebar_right_221045.html
│   ├───sidebar_right_221047.html
│   ├───sidebar_right_221049.html
│   ├───stock_movement.html
│   ├───stock_movement_20260316_104849.html
│   ├───stock_movement_20260316_123608.html
│   ├───stock_movement_221043.html
│   ├───stock_movement_221044.html
│   ├───stock_movement_221045.html
│   ├───stock_movement_221046.html
│   ├───stock_movement_221047.html
│   ├───stock_movement_221049.html
│   ├───stock_movement_form.html
│   ├───stock_movement_form_20260316_104849.html
│   ├───stock_movement_form_221044.html
│   ├───stock_movement_form_221045.html
│   ├───stock_movement_form_221046.html
│   ├───stock_movement_form_221047.html
│   ├───stock_movement_form_221049.html
│   ├───stock_overview.html
│   ├───stock_overview_20260316_104849.html
│   ├───stock_overview_20260316_123608.html
│   ├───stock_overview_221044.html
│   ├───stock_overview_221045.html
│   ├───stock_overview_221046.html
│   ├───stock_overview_221047.html
│   ├───stock_overview_221049.html
│   ├───stock_planning.html
│   ├───stock_planning_20260316_104849.html
│   ├───stock_planning_20260316_123608.html
│   ├───stock_planning_221044.html
│   ├───stock_planning_221045.html
│   ├───stock_planning_221046.html
│   ├───stock_planning_221047.html
│   ├───stock_planning_221049.html
│   ├───stock_purchasing.html
│   ├───stock_purchasing_20260316_104850.html
│   ├───stock_purchasing_20260316_123608.html
│   ├───stock_purchasing_221045.html
│   ├───stock_purchasing_221046.html
│   ├───stock_purchasing_221047.html
│   ├───stock_purchasing_221049.html
│   ├───system_status.html
│   ├───system_status_20260316_104852.html
│   ├───system_status_20260316_123608.html
│   ├───system_status_221045.html
│   ├───system_status_221047.html
│   ├───system_status_221050.html
│   ├───transaction_summary.html
│   ├───transaction_summary_20260316_104852.html
│   ├───transaction_summary_20260316_123608.html
│   ├───transaction_summary_221044.html
│   ├───transaction_summary_221046.html
│   ├───transaction_summary_221047.html
│   ├───transaction_summary_221050.html
│   ├───transfer_report.html
│   ├───transfer_report_20260316_104852.html
│   ├───transfer_report_20260316_123608.html
│   ├───transfer_report_221044.html
│   ├───transfer_report_221046.html
│   ├───transfer_report_221047.html
│   ├───transfer_report_221050.html
│   ├───unit_form.html
│   ├───unit_form_20260316_104850.html
│   ├───unit_form_20260316_123608.html
│   ├───unit_form_221044.html
│   ├───unit_form_221046.html
│   ├───unit_form_221047.html
│   ├───unit_form_221050.html
│   ├───units_list.html
│   ├───units_list_20260316_104850.html
│   ├───units_list_20260316_123608.html
│   ├───units_list_221044.html
│   ├───units_list_221045.html
│   ├───units_list_221046.html
│   ├───units_list_221047.html
│   ├───units_list_221050.html
│   ├───user_list.html
│   ├───user_list_20260316_104853.html
│   ├───user_list_20260316_123608.html
│   ├───user_list_221045.html
│   ├───user_list_221047.html
│   ├───user_list_221050.html
│   ├───user_roles_permissions.html
│   ├───user_roles_permissions_20260316_104853.html
│   ├───user_roles_permissions_20260316_123608.html
│   ├───user_roles_permissions_221045.html
│   ├───user_roles_permissions_221046.html
│   ├───user_roles_permissions_221047.html
│   ├───user_roles_permissions_221050.html
│   ├───users.html
│   ├───users_20260316_104852.html
│   ├───users_20260316_123608.html
│   ├───users_221044.html
│   ├───users_221045.html
│   ├───users_221047.html
│   ├───users_221050.html
│   ├───vendor_form.html
│   ├───vendor_form_20260316_104851.html
│   ├───vendor_form_20260316_123608.html
│   ├───vendor_form_221045.html
│   ├───vendor_form_221046.html
│   ├───vendor_form_221047.html
│   ├───vendor_form_221048.html
│   ├───vendor_form_221050.html
│   ├───vendor_list.html
│   ├───vendor_list_20260316_104851.html
│   ├───vendor_list_20260316_123608.html
│   ├───vendor_list_221046.html
│   ├───vendor_list_221047.html
│   ├───vendor_list_221048.html
│   ├───vendor_list_221050.html
│   ├───vendors_list.html
│   ├───vendors_list_20260316_104851.html
│   ├───vendors_list_20260316_123608.html
│   ├───vendors_list_221045.html
│   ├───vendors_list_221046.html
│   ├───vendors_list_221047.html
│   ├───vendors_list_221048.html
│   └───vendors_list_221050.html
├───_theme_backup/
│   └───20260314_083118/
│       └───lumra_pages/
│           ├───inventory/
│           ├───master_data/
│           └───reports/
├───_theme_migrate_backup/
│   ├───activity_log_20260316_123608.html
│   ├───add_campaign_20260316_123608.html
│   ├───approval_modal_20260316_123607.html
│   ├───base_report_20260316_123608.html
│   ├───business_feature_matrix_20260316_123608.html
│   ├───business_form_general_20260316_123608.html
│   ├───business_profile_20260316_123608.html
│   ├───business_settings_20260316_123608.html
│   ├───campaign_20260316_123608.html
│   ├───campaign_list_20260316_123608.html
│   ├───categories_list_20260316_123608.html
│   ├───contact_20260316_123608.html
│   ├───customer_detail_20260316_123608.html
│   ├───customer_form_20260316_123608.html
│   ├───customers_20260316_123608.html
│   ├───customers_list_20260316_123608.html
│   ├───dashboard_20260316_123608.html
│   ├───discount_20260316_123608.html
│   ├───error_404_20260316_123607.html
│   ├───error_500_20260316_123607.html
│   ├───financial_reports_20260316_123608.html
│   ├───kpi_card_white_20260316_123607.html
│   ├───location_list_20260316_123608.html
│   ├───locations_20260316_123608.html
│   ├───login_20260316_123607.html
│   ├───loyalty_members_20260316_123608.html
│   ├───market_insights_20260316_123608.html
│   ├───navbar_20260316_123607.html
│   ├───notification_20260316_123608.html
│   ├───pos_20260316_123608.html
│   ├───product_details_20260316_123608.html
│   ├───product_list_20260316_123608.html
│   ├───products_20260316_123608.html
│   ├───profile_20260316_123608.html
│   ├───purchasing_report_20260316_123608.html
│   ├───recipe_detail_20260316_123608.html
│   ├───recipe_form_20260316_123608.html
│   ├───recipe_list_20260316_123608.html
│   ├───report_activity_log_20260316_123608.html
│   ├───report_inventory_log_20260316_123608.html
│   ├───report_inventory_low_20260316_123608.html
│   ├───report_inventory_stock_20260316_123608.html
│   ├───report_profit_loss_detail_20260316_123608.html
│   ├───report_sales_by_outlet_20260316_123608.html
│   ├───report_sales_by_payment_20260316_123608.html
│   ├───report_sales_by_product_20260316_123608.html
│   ├───report_sales_summary_20260316_123608.html
│   ├───reporting_20260316_123608.html
│   ├───requisition_report_20260316_123608.html
│   ├───sales_history_20260316_123608.html
│   ├───sales_history_product_20260316_123608.html
│   ├───sales_intelligence_20260316_123608.html
│   ├───sales_performance_20260316_123608.html
│   ├───sales_report_20260316_123608.html
│   ├───search_20260316_123608.html
│   ├───settings_20260316_123608.html
│   ├───sidebar_right_20260316_123607.html
│   ├───stock_movement_20260316_123608.html
│   ├───stock_opname_20260316_123608.html
│   ├───stock_opname_approval_detail_20260316_123608.html
│   ├───stock_opname_approvals_20260316_123608.html
│   ├───stock_opname_form_20260316_123608.html
│   ├───stock_opname_locations_20260316_123608.html
│   ├───stock_opname_session_detail_20260316_123608.html
│   ├───stock_overview_20260316_123608.html
│   ├───stock_planning_20260316_123608.html
│   ├───stock_purchasing_20260316_123608.html
│   ├───supplier_price_confirm_delete_20260316_123608.html
│   ├───supplier_price_form_20260316_123608.html
│   ├───supplier_price_list_20260316_123608.html
│   ├───system_status_20260316_123608.html
│   ├───transaction_summary_20260316_123608.html
│   ├───transfer_report_20260316_123608.html
│   ├───trends_analysis_20260316_123608.html
│   ├───unit_form_20260316_123608.html
│   ├───units_list_20260316_123608.html
│   ├───user_list_20260316_123608.html
│   ├───user_roles_permissions_20260316_123608.html
│   ├───users_20260316_123608.html
│   ├───vendor_form_20260316_123608.html
│   ├───vendor_list_20260316_123608.html
│   └───vendors_list_20260316_123608.html
├───_token_migration_backup/
│   ├───20260318_092755/
│   │   ├───base.html
│   │   └───sidebar.html
│   └───templates/
│       ├───about_20260316_104852.html
│       ├───activity_drawer_20260316_104848.html
│       ├───add_campaign_20260316_104850.html
│       ├───add_stock_movement_20260316_104849.html
│       ├───approval_modal_20260316_104848.html
│       ├───base_20260316_104849.html
│       ├───base_report_20260316_104851.html
│       ├───business_feature_matrix_20260316_104852.html
│       ├───business_form_general_20260316_104852.html
│       ├───business_profile_20260316_104852.html
│       ├───business_settings_20260316_104852.html
│       ├───campaign_20260316_104850.html
│       ├───campaign_list_20260316_104850.html
│       ├───categories_list_20260316_104850.html
│       ├───category_form_20260316_104850.html
│       ├───customer_20260316_104850.html
│       ├───customer_detail_20260316_104850.html
│       ├───customer_form_20260316_104850.html
│       ├───customers_20260316_104850.html
│       ├───customers_list_20260316_104850.html
│       ├───dashboard_20260316_104852.html
│       ├───financial_reports_20260316_104852.html
│       ├───location_list_20260316_104850.html
│       ├───locations_20260316_104850.html
│       ├───login_20260316_104849.html
│       ├───market_insights_20260316_104852.html
│       ├───navbar_20260316_104849.html
│       ├───notification_20260316_104851.html
│       ├───pos_20260316_104852.html
│       ├───product_details_20260316_104849.html
│       ├───product_list_20260316_104849.html
│       ├───products_20260316_104849.html
│       ├───profile_20260316_104852.html
│       ├───purchasing_report_20260316_104851.html
│       ├───recipe_detail_20260316_104851.html
│       ├───recipe_form_20260316_104851.html
│       ├───recipe_list_20260316_104851.html
│       ├───register_20260316_104849.html
│       ├───report_inventory_log_20260316_104851.html
│       ├───report_inventory_low_20260316_104851.html
│       ├───report_inventory_stock_20260316_104851.html
│       ├───report_profit_loss_detail_20260316_104851.html
│       ├───report_sales_by_outlet_20260316_104851.html
│       ├───report_sales_by_payment_20260316_104851.html
│       ├───report_sales_by_product_20260316_104851.html
│       ├───report_sales_summary_20260316_104851.html
│       ├───reporting_20260316_104851.html
│       ├───requisition_report_20260316_104852.html
│       ├───sales_history_20260316_104852.html
│       ├───sales_history_product_20260316_104852.html
│       ├───sales_intelligence_20260316_104852.html
│       ├───sales_performance_20260316_104852.html
│       ├───sales_report_20260316_104852.html
│       ├───sidebar_20260316_104849.html
│       ├───sidebar_right_20260316_104849.html
│       ├───stock_movement_20260316_104849.html
│       ├───stock_movement_form_20260316_104849.html
│       ├───stock_opname_20260316_104850.html
│       ├───stock_opname_approval_detail_20260316_104849.html
│       ├───stock_opname_approvals_20260316_104849.html
│       ├───stock_opname_form_20260316_104849.html
│       ├───stock_opname_locations_20260316_104849.html
│       ├───stock_opname_session_detail_20260316_104850.html
│       ├───stock_overview_20260316_104849.html
│       ├───stock_planning_20260316_104849.html
│       ├───stock_purchasing_20260316_104850.html
│       ├───supplier_price_confirm_delete_20260316_104850.html
│       ├───supplier_price_form_20260316_104850.html
│       ├───supplier_price_list_20260316_104850.html
│       ├───system_status_20260316_104852.html
│       ├───transaction_summary_20260316_104852.html
│       ├───transfer_report_20260316_104852.html
│       ├───unit_form_20260316_104850.html
│       ├───units_list_20260316_104850.html
│       ├───user_list_20260316_104853.html
│       ├───user_roles_permissions_20260316_104853.html
│       ├───users_20260316_104852.html
│       ├───vendor_form_20260316_104851.html
│       ├───vendor_list_20260316_104851.html
│       └───vendors_list_20260316_104851.html
├───docs/
│   └───technical_doc.md
├───htmlcov/
│   ├───.gitignore
│   ├───class_index.html
│   ├───coverage_html_cb_188fc9a4.js
│   ├───favicon_32_cb_c827f16f.png
│   ├───function_index.html
│   ├───index.html
│   ├───keybd_closed_cb_900cfef5.png
│   ├───manage_py.html
│   ├───status.json
│   ├───style_cb_5c747636.css
│   ├───z_02df8607fdaf3af3___init___py.html
│   ├───z_02df8607fdaf3af3_currency_filters_py.html
│   ├───z_02df8607fdaf3af3_custom_filters_py.html
│   ├───z_02df8607fdaf3af3_custom_filters_settings_py.html
│   ├───z_46dc0a5042151c51___init___py.html
│   ├───z_46dc0a5042151c51_settings_py.html
│   ├───z_46dc0a5042151c51_urls_py.html
│   ├───z_5afb3b08a2d3bbd3___init___py.html
│   ├───z_5afb3b08a2d3bbd3_apps_py.html
│   ├───z_7ee2f61658cd33a0___init___py.html
│   ├───z_b2d61349199ef977___init___py.html
│   ├───z_b2d61349199ef977_admin_py.html
│   ├───z_b2d61349199ef977_apps_py.html
│   ├───z_b2d61349199ef977_middleware_py.html
│   ├───z_b2d61349199ef977_models_py.html
│   ├───z_b2d61349199ef977_signals_py.html
│   ├───z_d5c6799655c8c7f4___init___py.html
│   └───z_d5c6799655c8c7f4_logging_middleware_py.html
├───lumra_config/
│   ├───api/
│   │   ├───__init__.py
│   │   └───views.py
│   ├───auth_app/
│   │   ├───__init__.py
│   │   └───views.py
│   ├───forms/
│   │   └───__init__.py
│   ├───inventory/
│   │   ├───__init__.py
│   │   └───views.py
│   ├───marketing/
│   │   ├───__init__.py
│   │   └───views.py
│   ├───master_data/
│   │   ├───__init__.py
│   │   └───views.py
│   ├───production/
│   │   ├───__init__.py
│   │   └───views.py
│   ├───reports/
│   │   ├───__init__.py
│   │   └───views.py
│   ├───sales/
│   │   ├───__init__.py
│   │   └───views.py
│   ├───settings_app/
│   │   ├───__init__.py
│   │   └───views.py
│   ├───static/
│   │   └───css/
│   │       ├───lumra_design_system.css
│   │       └───theme_overrides.css
│   ├───templates/
│   │   ├───base/
│   │   │   ├───partials/
│   │   │   ├───activity_drawer.html
│   │   │   ├───alert.html
│   │   │   ├───alert_inner.html
│   │   │   ├───approval_modal.html
│   │   │   ├───base.html
│   │   │   ├───footer.html
│   │   │   ├───kpi_card.html
│   │   │   ├───kpi_card_inner.html
│   │   │   ├───kpi_card_white.html
│   │   │   ├───navbar.html
│   │   │   ├───sidebar.html
│   │   │   ├───sidebar1.html
│   │   │   ├───sidebar_item.html
│   │   │   └───sidebar_right.html
│   │   ├───lumra_pages/
│   │   │   ├───auth/
│   │   │   ├───etc/
│   │   │   ├───inventory/
│   │   │   ├───marketing/
│   │   │   ├───master_data/
│   │   │   ├───messages/
│   │   │   ├───production/
│   │   │   ├───reports/
│   │   │   ├───sales_insight/
│   │   │   └───settings/
│   │   └───dashboard.html.backup
│   ├───templatetags/
│   │   ├───__init__.py
│   │   ├───currency_filters.py
│   │   ├───custom_filters.py
│   │   └───custom_filters_settings.py
│   ├───tests/
│   │   ├───__init__.py
│   │   └───run_tests_report.py
│   ├───urls/
│   │   ├───campaigns.py
│   │   ├───discounts.py
│   │   ├───insights.py
│   │   ├───loyalty.py
│   │   ├───pages.py
│   │   ├───purchasing.py
│   │   ├───sales.py
│   │   ├───settings.py  ← database, middleware, templates
│   │   └───users.py
│   ├───views/
│   │   ├───__init__.py
│   │   ├───api_views.py
│   │   ├───auth_views.py
│   │   ├───customer_views.py
│   │   ├───dashboard_views.py
│   │   ├───helpers.py
│   │   ├───inventory_views.py
│   │   ├───masterdata_views.py
│   │   ├───misc_views.py
│   │   ├───pricing_views.py
│   │   ├───production_views.py
│   │   ├───report_views.py
│   │   ├───stock_movement_views.py
│   │   └───stock_opname_views.py
│   ├───__init__.py
│   ├───admin.py  ← Django admin registrations
│   ├───apps.py  ← AppConfig + signals ready()
│   ├───context_processors.py  ← app_version di semua template
│   ├───middleware.py  ← EnsureUserProfileMiddleware
│   ├───models.py  ← models
│   ├───signals.py  ← auto stock deduction
│   ├───tests.py
│   ├───utils.py
│   └───views.py
├───lumra_system/
│   ├───middleware/
│   │   ├───__init__.py
│   │   └───logging_middleware.py
│   ├───__init__.py
│   ├───asgi.py
│   ├───settings.py  ← database, middleware, templates
│   ├───urls.py  ← router utama
│   └───wsgi.py
├───reports/
│   ├───test_report_2026-03-11_15-30.md
│   ├───test_report_2026-03-11_15-33.md
│   └───test_report_2026-03-12_13-31.md
├───static/
│   └───css/
│       └───lumra_design_system.css
├───theme/
│   ├───static/
│   │   └───css/
│   │       └───dist/
│   ├───static_src/
│   │   ├───src/
│   │   │   └───styles.css
│   │   ├───.gitignore
│   │   ├───package-lock.json
│   │   ├───package.json
│   │   └───postcss.config.js
│   ├───templates/
│   │   ├───auth/
│   │   ├───components/
│   │   ├───includes/
│   │   └───base.html
│   ├───__init__.py
│   └───apps.py  ← AppConfig + signals ready()
├───tools/
│   ├───__init__.py
│   ├───read_logs.py
│   └───run_tests_report.py
├───.coverage
├───.lumra_consolidate_log.json
├───.lumra_dup_log.json
├───.lumra_fix_all_log.json
├───.lumra_master_log.json
├───.lumra_rename_log.json
├───.lumra_reorg_log.json
├───.lumra_root_cleanup_log.json
├───.lumra_sync_log.json
├───.lumra_theme_log.json
├───.migrate_templates_log.json
├───audit_report.json
├───blueprint.md
├───data_orang.xlsx
├───database.md
├───db.sqlite3
├───docs.md
├───filelist.txt
├───fix_render_paths.py
├───generate.md
├───generate_css.py
├───lumra.config.json
├───lumra_apply_theme.py
├───lumra_cleanup_duplicates.py
├───lumra_consolidate.py
├───lumra_css_scanner.py
├───lumra_design_system.css
├───lumra_doc_generator.py
├───lumra_emerald_upgrade.py
├───lumra_fix.py
├───lumra_fix_all_paths.py
├───lumra_fix_master.py
├───lumra_fix_master2.py
├───lumra_full_migrator.py
├───lumra_glass_audit.py
├───lumra_glass_audit_report.md
├───lumra_glass_fix.log
├───lumra_glass_fix.py
├───lumra_glass_fix_plan.md
├───lumra_include_scanner.py
├───lumra_logging.py
├───lumra_master.py
├───lumra_migrate_fix.py
├───lumra_mvc_align.py
├───lumra_recolor.py
├───lumra_rename.py
├───lumra_reorganize.py
├───lumra_root_cleanup.py
├───lumra_scanner.py
├───lumra_sync.py
├───lumra_sync_copy.py
├───lumra_template_audit3.py
├───lumra_template_cleaner.py
├───lumra_theme_migrate.py
├───lumra_theme_purchasing.py
├───lumra_token_migrator.py
├───lumra_ui_audit.py
├───lumra_ui_audit_data.json
├───lumra_ui_audit_report.md
├───manage.py
├───migrate_templates.py
├───out.json
├───package-lock.json
├───report.json
├───report.md
├───scan_result.md
├───seed_karyawan.py
├───seed_stores.py
├───strip_duplicates.py
└───validate.py
```

### Pola URL → View

Semua URL menggunakan `lazy_view()` untuk menghindari circular import:

```python
# lumra_system/urls.py
path('/', lazy_view('lumra_config.sales.views.dashboard_view'), name='dashboard')
#          └── lumra_config/sales/views.py (stub)
#                └── from lumra_config.views import dashboard_view
#                       └── lumra_config/views/dashboard_views.py
```


---

## 2. Database & Model

**Database**: PostgreSQL  
**App label**: `lumra_config`  
**Total model**: 25

| Model | Tabel PostgreSQL | Keterangan |
|-------|-----------------|------------|
| `Category` | `_categories` |  |
| `Vendor` | `_vendors` |  |
| `Tax` | `_taxes` |  |
| `Unit` | `_units` |  |
| `Location` | `lumra_config_locations` |  |
| `Product` | `lumra_config_products` |  |
| `ProductVariant` | `lumra_config_productvariants` |  |
| `ProductAttribute` | `lumra_config_productattribute_items` |  |
| `Stock` | `lumra_config_stock` |  |
| `Requisition` | `lumra_config_requisitions` |  |
| `RequisitionItem` | `lumra_config_requisitionitem` |  |
| `Transfer` | `lumra_config_transfers` |  |
| `TransferItem` | `lumra_config_transferitem` |  |
| `UserProfile` | `lumra_config_userprofile` |  |
| `Customer` | `lumra_config_customers` |  |
| `Order` | `lumra_config_orders` |  |
| `OrderItem` | `lumra_config_orderitems` |  |
| `ProductDetail` | `product_details_view` |  |
| `StockOpnameSession` | `lumra_config_stockopname_session` |  |
| `StockOpnameItem` | `lumra_config_stockopname_item` |  |
| `RecipeCategory` | `production_recipe_categories` |  ⚠️ *shared dengan core* |
| `Recipe` | `production_recipes` |  ⚠️ *shared dengan core* |
| `RecipeIngredient` | `production_recipe_ingredients` |  ⚠️ *shared dengan core* |
| `SupplierPrice` | `lumra_config_supplier_prices` |  |
| `SalesTarget` | `lumra_config_sales_targets` |  |

### Detail Field Model Utama

#### `Vendor` → tabel `_vendors`
| Field | Tipe |
|-------|------|
| `name` | `CharField` |
| `contact_person` | `CharField` |
| `phone` | `CharField` |
| `code` | `CharField` |
| `email` | `EmailField` |
| `address` | `TextField` |
| `tax_number` | `CharField` |
| `is_active` | `BooleanField` |
| `created_at` | `DateTimeField` |
| `updated_at` | `DateTimeField` |

#### `Location` → tabel `lumra_config_locations`
| Field | Tipe |
|-------|------|
| `name` | `CharField` |
| `address` | `TextField` |
| `location_type` | `CharField` |
| `created_at` | `DateTimeField` |

#### `Product` → tabel `lumra_config_products`
| Field | Tipe |
|-------|------|
| `name` | `CharField` |
| `description` | `TextField` |
| `category` | `ForeignKey` |
| `vendor` | `ForeignKey` |
| `tax` | `ForeignKey` |
| `unit` | `ForeignKey` |
| `created_at` | `DateTimeField` |
| `updated_at` | `DateTimeField` |

#### `ProductVariant` → tabel `lumra_config_productvariants`
| Field | Tipe |
|-------|------|
| `product` | `ForeignKey` |
| `sku` | `CharField` |
| `size_weight` | `CharField` |
| `price_buy` | `DecimalField` |
| `price_sell` | `DecimalField` |
| `updated_at` | `DateTimeField` |

#### `Stock` → tabel `lumra_config_stock`
| Field | Tipe |
|-------|------|
| `variant` | `ForeignKey` |
| `location` | `ForeignKey` |
| `quantity` | `IntegerField` |
| `transaction_type` | `CharField` |
| `notes` | `TextField` |
| `last_updated` | `DateTimeField` |
| `created_at` | `DateTimeField` |

#### `UserProfile` → tabel `lumra_config_userprofile`
| Field | Tipe |
|-------|------|
| `user` | `OneToOneField` |
| `location` | `ForeignKey` |

#### `Customer` → tabel `lumra_config_customers`
| Field | Tipe |
|-------|------|
| `name` | `CharField` |
| `email` | `EmailField` |
| `phone` | `CharField` |
| `address` | `TextField` |
| `city` | `CharField` |
| `tier` | `CharField` |
| `loyalty_points` | `IntegerField` |
| `total_spent` | `DecimalField` |
| `total_orders` | `IntegerField` |
| `is_active` | `BooleanField` |
| `created_at` | `DateTimeField` |
| `updated_at` | `DateTimeField` |
| `last_order_date` | `DateTimeField` |

#### `Order` → tabel `lumra_config_orders`
| Field | Tipe |
|-------|------|
| `customer` | `ForeignKey` |
| `customer_name` | `CharField` |
| `status` | `CharField` |
| `created_at` | `DateTimeField` |

#### `OrderItem` → tabel `lumra_config_orderitems`
| Field | Tipe |
|-------|------|
| `order` | `ForeignKey` |
| `variant` | `ForeignKey` |
| `quantity` | `PositiveIntegerField` |
| `price` | `DecimalField` |

#### `Recipe` → tabel `production_recipes`
| Field | Tipe |
|-------|------|
| `name` | `CharField` |
| `description` | `TextField` |
| `instructions` | `TextField` |
| `category` | `ForeignKey` |
| `yield_quantity` | `DecimalField` |
| `yield_unit` | `ForeignKey` |
| `preparation_time` | `IntegerField` |
| `total_cost` | `DecimalField` |
| `cost_per_unit` | `DecimalField` |
| `is_archived` | `BooleanField` |
| `created_at` | `DateTimeField` |
| `updated_at` | `DateTimeField` |

> ⚠️ **Tabel shared** (`production_*`) namanya sama antara `core` dan `lumra`.
> Saat migrate gunakan `--fake-initial` agar tidak error DuplicateTable.


---

## 3. URL → View → Template

Total: **115 URL** aktif

### 🛒 Sales & POS

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/notification/` | GET | `notification_view` | `notification.html` | 🌐 |
| `/notifications/` | GET | `as_viewurlnotification` | `—` | 🌐 |
| `/sales/pos/` | GET | `pos_view` | `pos.html` | 🌐 |
| `/sales/pos/create-order/` | GET, POST | `pos_create_order` | `purchasing.html` | 🌐 |
| `/sales/history/` | GET | `sales_history_view` | `—` | 🌐 |
| `/sales/history/products/` | GET | `sales_history_products_view` | `sales_history_product.html` | 🌐 |
| `/sales/performance/` | GET, POST | `sales_performance_view` | `—` | 🌐 |
| `/purchasing/` | GET | `purchasing_view` | `purchasing.html` | 🌐 |
| `/insights/sales_insight/` | GET | `sales_insight_view` | `—` | 🌐 |
| `/reports/sales/` | GET | `sales_report` | `sales_report.html` | 🌐 |
| `/reports/purchasing/` | GET | `purchasing_report` | `purchasing_report.html` | 🌐 |
| `/reports/sales-by-outlet/` | GET | `report_sales_by_outlet` | `report_sales_by_outlet.html` | 🌐 |
| `/reports/sales-by-payment/` | GET | `report_sales_by_payment` | `report_sales_by_payment.html` | 🌐 |
| `/reports/sales-by-product/` | GET | `report_sales_by_product` | `report_sales_by_product.html` | 🌐 |
| `/reports/sales-summary/` | GET | `report_sales_summary` | `report_sales_summary.html` | 🌐 |
| `/api/dashboard/data/` | GET | `api_dashboard_data` | `—` | 🌐 |
| `/api/dashboard/chart-data/` | GET | `api_dashboard_chart_data` | `—` | 🌐 |

### 📦 Master Data

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/customers/` | GET | `as_viewurlmastercustomers` | `—` | 🌐 |
| `/inventory/products/` | GET | `as_viewurlmasterproducts` | `—` | 🌐 |
| `/inventory/products/<int:product_id>/` | GET | `as_viewurlmasterproductsproduct_id` | `—` | 🌐 |
| `/master/products/` | GET | `products_view` | `products.html` | 🌐 |
| `/master/products/<int:product_id>/` | GET | `product_detail_view` | `product_details.html` | 🌐 |
| `/master/products/import-template/` | GET | `products_import_template` | `—` | 🌐 |
| `/master/categories/` | GET | `categories_list` | `categories_list.html` | 🌐 |
| `/master/categories/add/` | GET, POST | `category_create` | `category_form.html` | 🌐 |
| `/master/categories/<int:pk>/edit/` | GET, POST | `category_update` | `category_form.html` | 🌐 |
| `/master/categories/<int:pk>/delete/` | GET | `category_delete` | `units_list.html` | 🌐 |
| `/master/units/` | GET | `units_list` | `units_list.html` | 🌐 |
| `/master/units/add/` | GET, POST | `unit_create` | `unit_form.html` | 🌐 |
| `/master/units/<int:pk>/edit/` | GET, POST | `unit_update` | `unit_form.html` | 🌐 |
| `/master/units/<int:pk>/delete/` | GET | `unit_delete` | `vendors_list.html` | 🌐 |
| `/master/vendors/` | GET | `vendors_list` | `vendors_list.html` | 🌐 |
| `/master/vendors/add/` | GET, POST | `vendor_create` | `vendor_form.html` | 🌐 |
| `/master/vendors/<int:pk>/edit/` | GET, POST | `vendor_update` | `vendor_form.html` | 🌐 |
| `/master/vendors/<int:pk>/delete/` | GET | `vendor_delete` | `—` | 🌐 |
| `/master/customers/` | GET | `customer_list` | `customers_list.html` | 🌐 |
| `/master/customers/add/` | GET, POST | `customer_create` | `customer_form.html` | 🌐 |
| `/master/customers/<int:pk>/` | GET | `customer_detail` | `customer_detail.html` | 🌐 |
| `/master/customers/<int:pk>/edit/` | GET, POST | `customer_update` | `customer_form.html` | 🌐 |
| `/master/customers/<int:pk>/delete/` | GET | `customer_delete` | `—` | 🌐 |
| `/master/customers/<int:pk>/redeem/` | GET | `customer_redeem_points` | `—` | 🌐 |
| `/master/stock-opname/` | GET | `stock_opname_locations` | `stock_opname_locations.html` | 🌐 |
| `/master/stock-opname/<int:location_id>/form/` | GET, POST | `stock_opname_form` | `—` | 🌐 |
| `/master/stock-opname/approvals/` | GET | `stock_opname_approvals` | `stock_opname_approvals.html` | 🌐 |
| `/master/stock-opname/approvals/<int:session_id>/` | GET | `stock_opname_approval_detail` | `stock_opname_approval_detail.html` | 🌐 |

### 🏭 Inventory

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/inventory/planning/` | GET | `stock_planning_view` | `stock_planning.html` | 🌐 |
| `/inventory/movement/` | GET | `stock_movement_view` | `stock_movement.html` | 🌐 |
| `/inventory/movement/add/` | GET, POST | `add_stock_movement_view` | `add_stock_movement.html` | 🌐 |
| `/inventory/movement/export/` | GET | `export_stock_movement` | `stock_movement.html` | 🌐 |
| `/inventory/supplier-prices/` | GET | `supplier_price_list` | `supplier_price_list.html` | 🌐 |
| `/inventory/supplier-prices/form/` | GET, POST | `supplier_price_form` | `supplier_price_form.html` | 🌐 |
| `/inventory/supplier-prices/<int:price_id>/delete/` | GET | `supplier_price_delete` | `supplier_price_confirm_delete.html` | 🌐 |
| `/reports/requisitions/` | GET | `requisition_report` | `requisition_report.html` | 🌐 |
| `/reports/inventory-log/` | GET | `report_inventory_log` | `report_inventory_log.html` | 🌐 |
| `/reports/inventory-low/` | GET | `report_inventory_low` | `report_inventory_low.html` | 🌐 |
| `/reports/inventory-stock/` | GET | `report_inventory_stock` | `report_inventory_stock.html` | 🌐 |
| `/api/requisition/submit/` | GET, POST | `submit_requisition` | `—` | 🌐 |
| `/api/requisition/<int:requisition_id>/approve/` | GET | `approve_requisition` | `—` | 🌐 |
| `/api/submit-stock-allocation/` | GET, POST | `submit_stock_allocation` | `—` | 🌐 |
| `/api/location-stock/<str:product_sku>/` | GET | `get_location_stock` | `—` | 🌐 |

### ⚗️ Production

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/production/recipes/` | GET | `recipe_list` | `recipe_list.html` | 🌐 |
| `/production/recipes/form/` | GET, POST | `recipe_form` | `recipe_form.html` | 🌐 |
| `/production/recipes/<int:recipe_id>/` | GET | `recipe_detail` | `recipe_detail.html` | 🌐 |
| `/production/recipes/<int:recipe_id>/edit/` | GET, POST | `recipe_form` | `recipe_form.html` | 🌐 |
| `/production/recipes/<int:recipe_id>/delete/` | GET | `recipe_delete` | `—` | 🌐 |
| `/production/recipes/<int:recipe_id>/delete-legacy/` | GET | `recipe_delete` | `—` | 🌐 |

### 📣 Marketing

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/marketing/campaigns/` | GET | `campaign_list_view` | `campaign.html` | 🌐 |
| `/marketing/campaigns/add/` | GET, POST | `add_campaign_view` | `campaign.html` | 🌐 |
| `/marketing/campaigns/<int:campaign_id>/edit/` | GET, POST | `edit_campaign_view` | `campaign.html` | 🌐 |
| `/marketing/campaigns/<int:campaign_id>/delete/` | GET | `delete_campaign_view` | `campaign.html` | 🌐 |
| `/campaigns/` | GET | `as_viewurlmarketingcampaigns` | `—` | 🌐 |
| `/campaigns/add/` | GET, POST | `as_viewurlmarketingcampaignsadd` | `—` | 🌐 |
| `/marketing/discounts/` | GET | `discount_list_view` | `discount.html` | 🌐 |
| `/marketing/discounts/add/` | GET, POST | `add_discount_view` | `discount.html` | 🌐 |
| `/marketing/discounts/<int:discount_id>/edit/` | GET, POST | `edit_discount_view` | `discount.html` | 🌐 |
| `/marketing/discounts/<int:discount_id>/delete/` | GET | `delete_discount_view` | `discount.html` | 🌐 |
| `/discounts/` | GET | `as_viewurlmarketingdiscounts` | `—` | 🌐 |
| `/discounts/add/` | GET, POST | `as_viewurlmarketingdiscountsadd` | `—` | 🌐 |
| `/marketing/loyalty/` | GET | `loyalty_members_view` | `loyalty_members.html` | 🌐 |
| `/marketing/loyalty/add/` | GET, POST | `add_loyalty_member_view` | `loyalty_members.html` | 🌐 |
| `/marketing/loyalty/<int:member_id>/edit/` | GET, POST | `edit_loyalty_member_view` | `loyalty_members.html` | 🌐 |
| `/marketing/loyalty/<int:member_id>/delete/` | GET | `delete_loyalty_member_view` | `loyalty_members.html` | 🌐 |
| `/loyalty/` | GET | `as_viewurlmarketingloyalty` | `—` | 🌐 |
| `/loyalty/add/` | GET, POST | `as_viewurlmarketingloyaltyadd` | `—` | 🌐 |

### 📊 Reports & Insights

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/insights/financial/` | GET | `financial_reports_view` | `—` | 🌐 |
| `/insights/market/` | GET | `market_insights_view` | `—` | 🌐 |
| `/insights/trends/` | GET | `trends_analysis_view` | `trends_analysis.html` | 🌐 |
| `/insights/activity/` | GET | `activity_log_view` | `activity_log.html` | 🌐 |
| `/insights/download-report/<str:report_type>/` | GET | `download_report_view` | `market_insights.html` | 🌐 |
| `/insights/export-trends/<str:trend_type>/` | GET | `export_trends_view` | `trends_analysis.html` | 🌐 |
| `/reports/transactions/` | GET | `transaction_summary` | `transaction_summary.html` | 🌐 |
| `/reports/transfers/` | GET | `transfer_report` | `transfer_report.html` | 🌐 |
| `/reports/profit-loss-detail/` | GET | `report_profit_loss_detail` | `report_profit_loss_detail.html` | 🌐 |
| `/api/transfer/<int:transfer_id>/confirm/` | GET | `confirm_receipt` | `—` | 🌐 |

### ⚙️ Settings & Users

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/users/` | GET | `users_view` | `error_403.html` | 🌐 |
| `/profile/` | GET | `profile_view` | `profile.html` | 🌐 |
| `/settings/` | GET | `settings_view` | `settings.html` | 🌐 |
| `/settings/system/` | GET | `system_status_view` | `system_status.html` | 🌐 |
| `/settings/business/` | GET | `business_settings_view` | `business_settings.html` | 🌐 |
| `/settings/business/general/` | GET, POST | `business_form_general_view` | `business_form_general.html` | 🌐 |
| `/settings/business/feature-matrix/` | GET | `business_feature_matrix_view` | `business_feature_matrix.html` | 🌐 |
| `/settings/business/roles/` | GET | `user_roles_permissions_view` | `user_roles_permissions.html` | 🌐 |
| `/about/` | GET | `about_view` | `about.html` | 🌐 |
| `/contact/` | GET | `contact_view` | `contact.html` | 🌐 |
| `/pricing/` | GET | `pricing_view` | `—` | 🌐 |
| `/search/` | GET | `search_view` | `search.html` | 🌐 |

### 🔐 Authentication

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/accounts/login/` | GET | `as_viewurlauthlogin` | `—` | 🔒 |
| `/auth/login/` | GET | `login_view` | `login.html` | 🔒 |
| `/auth/logout/` | GET | `logout_view` | `profile.html` | 🌐 |

### 🔌 Internal API

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/api/purchases/submit/` | GET, POST | `submit_purchases` | `—` | 🌐 |
| `/api/products/import/` | GET | `products_import` | `—` | 🌐 |

### 🌐 Lainnya

| URL | Method | View Function | Template | Auth |
|-----|--------|---------------|----------|------|
| `/admin/` | GET | `urls` | `—` | 🌐 |
| `/home/` | GET | `as_viewurl` | `—` | 🌐 |
| `/locations/` | GET | `locations_view` | `locations.html` | 🌐 |
| `/__reload__/` | GET | `urls` | `—` | 🌐 |

> 🔒 = Login required &nbsp;&nbsp; 🌐 = Public


---

## 4. Settings & Konfigurasi

File: `lumra_system/settings.py`

### Database
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lumra_set_allegra', # Nama database Anda
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Middleware (urutan penting!)
```python
MIDDLEWARE = [
    'lumra_system.middleware.logging_middleware.LumraRequestLoggingMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Pastikan setiap user login punya UserProfile (dibutuhkan oleh templates)
    'lumra_config.middleware.EnsureUserProfileMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### INSTALLED_APPS
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'tailwind',
    'theme',  # Ini nama aplikasi CSS yang akan kita buat
    'django_browser_reload',
    'lumra_config',
]
```


---

## 5. Template Audit

**Total template**: 102  
**Punya inline CSS**: 81  
**Punya KPI/card inline** (bukan via include): 41  
**Pakai include**: 4  
**Standalone** (tidak extend apapun): 0

### ⚠️ Template dengan KPI/Card Inline (perlu refactor)

> Template ini render KPI card **langsung** tanpa include.
> Jika ingin mengubah desain card, perlu edit setiap file ini satu per satu.

| Template | Extends | Inline Classes |
|----------|---------|----------------|
| `base\base.html` | — | `skip-link`, `sidebar-open`, `header-shift`, `header-shift`, `header-shift` +12 lainnya |
| `base\kpi_card.html` | — |  |
| `base\kpi_card_inner.html` | — |  |
| `base\kpi_card_white.html` | — |  |
| `base\sidebar.html` | — | `sidebar-glass`, `nav-item`, `collapsed`, `active`, `parent-active` +21 lainnya |
| `base\sidebar1.html` | — | `sidebar-glass`, `nav-item`, `collapsed`, `active`, `parent-active` +21 lainnya |
| `lumra_pages\inventory\product_details.html` | `base/base.html` | `modal-overlay`, `panel-glass`, `bg-blob-4`, `modal-box` |
| `lumra_pages\marketing\campaign.html` | `lumra_pages/reports/base_report.html` | `status-active`, `status-paused`, `status-completed`, `status-draft`, `type-badge` +20 lainnya |
| `lumra_pages\marketing\campaign_list.html` | `lumra_pages/reports/base_report.html` | `status-active`, `status-paused`, `status-completed`, `status-draft`, `type-badge` +20 lainnya |
| `lumra_pages\master_data\customer_detail.html` | `lumra_pages/reports/base_report.html` | `profile-card`, `tab-bar`, `tab-btn`, `active`, `section-card` +20 lainnya |
| `lumra_pages\master_data\customers.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `tier-btn` +23 lainnya |
| `lumra_pages\master_data\customers_list.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `tier-btn` +23 lainnya |
| `lumra_pages\master_data\location_list.html` | `base/base.html` | `pac-container`, `live-dot`, `live-dot-emerald`, `card-img-wrap`, `card-img-overlay` +4 lainnya |
| `lumra_pages\master_data\locations.html` | `base/base.html` | `pac-container`, `live-dot`, `live-dot-emerald`, `card-img-wrap`, `card-img-overlay` +4 lainnya |
| `lumra_pages\reports\purchasing_report.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\report_inventory_log.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\report_inventory_low.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\report_inventory_stock.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\report_profit_loss_detail.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\report_sales_by_outlet.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\report_sales_by_payment.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\report_sales_by_product.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\report_sales_summary.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\reporting.html` | `base/base.html` |  |
| `lumra_pages\reports\requisition_report.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\sales_history.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\sales_history_product.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\sales_report.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\sales_report_after.html` | `lumra_pages/reports/base_report.html` |  |
| `lumra_pages\reports\transaction_summary.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\reports\transfer_report.html` | `lumra_pages/reports/base_report.html` | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill` +21 lainnya |
| `lumra_pages\sales_insight\dashboard.html` | `base/base.html` | `chart-card`, `side-card`, `perf-strip`, `metric-strip`, `metric-icon` +6 lainnya |
| `lumra_pages\sales_insight\financial_reports.html` | `base/base.html` | `bar-divider`, `date-pill`, `active`, `highlight-pulse`, `expect-card` +3 lainnya |
| `lumra_pages\sales_insight\market_insights.html` | `base/base.html` | `bar-divider`, `date-pill`, `active`, `highlight-pulse`, `heatmap-grid` +14 lainnya |
| `lumra_pages\sales_insight\pos.html` | `base/base.html` | `product-tile`, `out-of-stock`, `order-row`, `qty-btn`, `pay-pill` +15 lainnya |
| `lumra_pages\sales_insight\sales_performance.html` | `lumra_pages/reports/base_report.html` | `back-banner`, `modal-overlay`, `modal-card`, `tier-badge`, `tier-platinum` +9 lainnya |
| `lumra_pages\settings\business_feature_matrix.html` | `base/base.html` | `feat-card`, `active`, `locked`, `ftog`, `on` +15 lainnya |
| `lumra_pages\settings\settings.html` | `base/base.html` |  |
| `lumra_pages\settings\user_list.html` | `base/base.html` | `ring-superadmin`, `ring-admin`, `ring-manager`, `ring-staff`, `ring-viewer` +18 lainnya |
| `lumra_pages\settings\user_roles_permissions.html` | `base/base.html` | `perm-toggle`, `on`, `off`, `knob`, `knob` +18 lainnya |
| `lumra_pages\settings\users.html` | `base/base.html` | `ring-superadmin`, `ring-admin`, `ring-manager`, `ring-staff`, `ring-viewer` +18 lainnya |

### ✅ Template yang Sudah Pakai include

| Template | Include |
|----------|---------|
| `base\alert.html` | `base/alert_inner.html`, `base/alert_inner.html`, `base/alert_inner.html` +1 |
| `base\base.html` | `base/sidebar.html`, `base/navbar.html`, `base/footer.html` |
| `base\partials\bg_blob.html` | `base/partials/bg_blob.html` |
| `lumra_pages\sales_insight\dashboard.html` | `base/sidebar_right.html` |

### 🔶 Template dengan Banyak CSS Inline

| Template | Jumlah Class | Classes |
|----------|-------------|----------|
| `lumra_pages\sales_insight\sales_intelligence.html` | 44 | `sh-bg-orb`, `sh-bg-orb-1`, `sh-bg-orb-2`, `sh-bg-orb-3`, `summary-band`, `stat-cell` |
| `lumra_pages\settings\about.html` | 44 | `about-page`, `display-font`, `glass-dark`, `hero-section`, `hero-eyebrow`, `hero-title` |
| `lumra_pages\inventory\add_stock_movement.html` | 39 | `form-card`, `theme-in`, `theme-out`, `theme-adj`, `card-glow`, `lbl` |
| `lumra_pages\inventory\stock_movement_form.html` | 39 | `form-card`, `theme-in`, `theme-out`, `theme-adj`, `card-glow`, `lbl` |
| `lumra_pages\inventory\stock_movement.html` | 30 | `stat-card`, `stat-icon`, `amber-pulse`, `search-input`, `mov-row`, `pill` |
| `lumra_pages\inventory\product_list.html` | 28 | `s-input`, `stat-card`, `tbl-head`, `tbl-th`, `sortable`, `tbl-row` |
| `lumra_pages\inventory\products.html` | 28 | `s-input`, `stat-card`, `tbl-head`, `tbl-th`, `sortable`, `tbl-row` |
| `lumra_pages\master_data\customers.html` | 28 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `tier-btn`, `active-regular` |
| `lumra_pages\master_data\customers_list.html` | 28 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `tier-btn`, `active-regular` |
| `base\sidebar.html` | 26 | `sidebar-glass`, `nav-item`, `collapsed`, `active`, `parent-active`, `nav-icon-wrap` |
| `base\sidebar1.html` | 26 | `sidebar-glass`, `nav-item`, `collapsed`, `active`, `parent-active`, `nav-icon-wrap` |
| `lumra_pages\reports\purchasing_report.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\report_inventory_log.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\report_inventory_low.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\report_inventory_stock.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\report_profit_loss_detail.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\report_sales_by_outlet.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\report_sales_by_payment.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\report_sales_by_product.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\report_sales_summary.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\requisition_report.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\sales_history.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\sales_history_product.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\sales_report.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\transaction_summary.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\reports\transfer_report.html` | 26 | `bar-divider`, `bar-input`, `bar-input-wrap`, `bar-select`, `date-pill`, `has-range` |
| `lumra_pages\settings\business_settings.html` | 26 | `sub-banner`, `sub-glow`, `badge`, `badge-titan`, `badge-warehouse`, `badge-boutique` |
| `lumra_pages\settings\system_status.html` | 26 | `health-card`, `badge`, `badge-ok`, `badge-warn`, `badge-error`, `badge-info` |
| `lumra_pages\marketing\campaign.html` | 25 | `status-active`, `status-paused`, `status-completed`, `status-draft`, `type-badge`, `type-discount` |
| `lumra_pages\marketing\campaign_list.html` | 25 | `status-active`, `status-paused`, `status-completed`, `status-draft`, `type-badge`, `type-discount` |
| `lumra_pages\master_data\customer_detail.html` | 25 | `profile-card`, `tab-bar`, `tab-btn`, `active`, `section-card`, `data-row` |
| `lumra_pages\marketing\add_campaign.html` | 23 | `f-hint`, `promo-card`, `selected`, `card-icon`, `check`, `check` |
| `lumra_pages\master_data\vendor_form.html` | 23 | `mono`, `hero-card`, `big-avatar`, `stat-card`, `perf-track`, `perf-fill` |
| `lumra_pages\settings\user_list.html` | 23 | `ring-superadmin`, `ring-admin`, `ring-manager`, `ring-staff`, `ring-viewer`, `rbadge` |
| `lumra_pages\settings\user_roles_permissions.html` | 23 | `perm-toggle`, `on`, `off`, `knob`, `knob`, `knob` |
| `lumra_pages\settings\users.html` | 23 | `ring-superadmin`, `ring-admin`, `ring-manager`, `ring-staff`, `ring-viewer`, `rbadge` |
| `lumra_pages\master_data\customer_form.html` | 22 | `form-card`, `field-group`, `field-label`, `field-input`, `no-icon`, `field-icon` |
| `lumra_pages\master_data\vendor_list.html` | 22 | `mono`, `glass-deep`, `v-avatar`, `badge-verified`, `badge-preferred`, `badge-pending` |
| `lumra_pages\master_data\vendors_list.html` | 22 | `mono`, `glass-deep`, `v-avatar`, `badge-verified`, `badge-preferred`, `badge-pending` |
| `lumra_pages\sales_insight\pos.html` | 20 | `product-tile`, `out-of-stock`, `order-row`, `qty-btn`, `pay-pill`, `active` |
| `lumra_pages\settings\business_feature_matrix.html` | 20 | `feat-card`, `active`, `locked`, `ftog`, `on`, `off` |
| `lumra_pages\master_data\unit_form.html` | 19 | `mono-inp`, `err-msg`, `hint`, `lbl`, `grp-pill`, `active` |
| `lumra_pages\master_data\units_list.html` | 19 | `stat-card`, `stat-icon`, `filter-tab`, `active`, `search-input`, `unit-row` |
| `lumra_pages\sales_insight\market_insights.html` | 19 | `bar-divider`, `date-pill`, `active`, `highlight-pulse`, `heatmap-grid`, `heatmap-cell` |
| `lumra_pages\messages\notification.html` | 18 | `stat-card`, `stat-icon`, `filter-tab`, `active`, `search-input`, `msg-row` |
| `base\base.html` | 17 | `skip-link`, `sidebar-open`, `header-shift`, `header-shift`, `header-shift`, `content-shift` |
| `base\navbar.html` | 16 | `nav-glass`, `cmd-input`, `cmd-token`, `cmd-token-product`, `cmd-token-location`, `cmd-token-stock` |
| `lumra_pages\inventory\stock_planning.html` | 16 | `stat-card`, `stat-icon`, `pulse-glow`, `product-row`, `selected`, `search-input` |
| `lumra_pages\inventory\stock_purchasing.html` | 16 | `stat-card`, `stat-icon`, `pulse-glow`, `product-row`, `selected`, `search-input` |
| `lumra_pages\settings\business_form_general.html` | 16 | `lbl`, `err-msg`, `logo-drop`, `drag`, `swatch`, `selected` |
| `lumra_pages\settings\business_profile.html` | 16 | `lbl`, `err-msg`, `logo-drop`, `drag`, `swatch`, `selected` |
| `base\activity_drawer.html` | 15 | `drawer-backdrop`, `drawer-panel`, `open`, `drawer-status-new`, `drawer-status-transit`, `drawer-status-critical` |
| `lumra_pages\sales_insight\sales_performance.html` | 14 | `back-banner`, `modal-overlay`, `modal-card`, `tier-badge`, `tier-platinum`, `tier-gold` |
| `lumra_pages\settings\profile.html` | 14 | `avatar-ring`, `info-row`, `tab-btn`, `active`, `act-item`, `toggle-track` |
| `lumra_pages\master_data\categories_list.html` | 13 | `s-input`, `tbl-head`, `tbl-th`, `sortable`, `tbl-row`, `swatch` |
| `base\approval_modal.html` | 12 | `approval-overlay`, `approval-backdrop`, `approval-box`, `approval-stripe`, `stripe-new`, `stripe-critical` |
| `lumra_pages\sales_insight\dashboard.html` | 11 | `chart-card`, `side-card`, `perf-strip`, `metric-strip`, `metric-icon`, `prod-row` |
| `base\sidebar_right.html` | 9 | `activity-item`, `activity-item`, `activity-dot-wrap`, `activity-dot`, `chip-slate`, `activity-new` |
| `lumra_pages\master_data\location_list.html` | 9 | `pac-container`, `live-dot`, `live-dot-emerald`, `card-img-wrap`, `card-img-overlay`, `map-legend` |
| `lumra_pages\master_data\locations.html` | 9 | `pac-container`, `live-dot`, `live-dot-emerald`, `card-img-wrap`, `card-img-overlay`, `map-legend` |
| `lumra_pages\auth\login.html` | 8 | `auth-page-bg`, `auth-blob`, `auth-blob-1`, `auth-blob-2`, `auth-blob-3`, `auth-card` |
| `lumra_pages\auth\register.html` | 8 | `auth-page-bg`, `auth-blob`, `auth-blob-1`, `auth-blob-2`, `auth-blob-3`, `auth-card` |
| `lumra_pages\master_data\category_form.html` | 8 | `f-error`, `char-counter`, `warn`, `slug-badge`, `color-swatch`, `selected` |
| `lumra_pages\sales_insight\financial_reports.html` | 8 | `bar-divider`, `date-pill`, `active`, `highlight-pulse`, `expect-card`, `placeholder-badge` |
| `lumra_pages\inventory\product_details.html` | 4 | `modal-overlay`, `panel-glass`, `bg-blob-4`, `modal-box` |
| `lumra_pages\inventory\stock_overview.html` | 4 | `modal-overlay`, `panel-glass`, `bg-blob-4`, `modal-box` |


---


*Dokumentasi ini dibuat otomatis dari source code lumra_config ERP.*
