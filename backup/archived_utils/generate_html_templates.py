#!/usr/bin/env python
"""
HTML Template Generator untuk LUMRA ERP
Generator ini membuat semua file HTML kosong dengan template pattern yang konsisten
"""

import os
from pathlib import Path

BASE_PATH = Path("lumra_config/templates/lumra_pages")

# Template patterns untuk berbagai tipe halaman

TEMPLATE_LIST = '''{% extends 'base/base.html' %}

{% block title %}{{ page_title }} - LUMRA{% endblock %}

{% block content %}
  {% include 'base/navbar.html' %}
  {% include 'base/sidebar.html' %}

  <div class="main-content px-6 py-6">
    <!-- Breadcrumb -->
    {% include 'base/partials/breadcrumb.html' with breadcrumb_items=breadcrumb %}

    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-3xl font-bold text-slate-100">{{ page_title }}</h1>
        <p class="text-slate-400">{{ page_description }}</p>
      </div>
      {% if add_button_url %}
        <a href="{{ add_button_url }}" class="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-lg transition">
          <i class="fas fa-plus mr-2"></i> Tambah Baru
        </a>
      {% endif %}
    </div>

    <!-- Search & Filter -->
    <div class="mb-6 flex gap-4">
      <input type="text" placeholder="Cari..." class="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-emerald-500">
      <button class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-100 rounded-lg transition">
        <i class="fas fa-search"></i>
      </button>
    </div>

    <!-- Data Table -->
    {% if items %}
      {% include 'base/partials/data_table.html' with table_columns=columns table_rows=items %}
      
      <!-- Pagination -->
      {% if page_obj %}
        {% include 'base/partials/pagination.html' %}
      {% endif %}
    {% else %}
      {% include 'base/partials/empty_state.html' with title="Tidak ada data" message="Mulai dengan membuat item baru." button_text="Tambah Item" button_url=add_button_url %}
    {% endif %}
  </div>
{% endblock %}
'''

TEMPLATE_FORM = '''{% extends 'base/base.html' %}

{% block title %}{{ form_title }} - LUMRA{% endblock %}

{% block content %}
  {% include 'base/navbar.html' %}
  {% include 'base/sidebar.html' %}

  <div class="main-content px-6 py-6">
    <!-- Breadcrumb -->
    {% include 'base/partials/breadcrumb.html' with breadcrumb_items=breadcrumb %}

    <!-- Form Card -->
    <div class="bg-gradient-to-b from-slate-900 to-slate-800 rounded-lg border border-slate-700 max-w-2xl shadow-lg overflow-hidden">
      <!-- Header -->
      <div class="bg-gradient-to-r from-emerald-900/30 to-slate-900 px-8 py-6 border-b border-slate-700">
        <h1 class="text-2xl font-bold text-emergald-400">{{ form_title }}</h1>
      </div>

      <!-- Form -->
      <form method="post" class="p-8 space-y-6" enctype="multipart/form-data">
        {% csrf_token %}

        {% if form_errors %}
          <div class="p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">
            {{ form_errors }}
          </div>
        {% endif %}

        <!-- Form fields go here -->
        <div class="space-y-4">
          <!-- Template for form fields -->
          {% for field in form %}
            {% include 'base/partials/form_field.html' with field_type='text' label=field.label name=field.name %}
          {% endfor %}
        </div>

        <!-- Submit Buttons -->
        <div class="flex gap-3 pt-6 border-t border-slate-700">
          <button type="submit" class="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-lg transition">
            <i class="fas fa-check mr-2"></i> Simpan
          </button>
          <a href="{% url list_view_name %}" class="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-slate-100 font-semibold rounded-lg transition">
            <i class="fas fa-times mr-2"></i> Batal
          </a>
        </div>
      </form>
    </div>
  </div>
{% endblock %}
'''

TEMPLATE_DETAIL = '''{% extends 'base/base.html' %}

{% block title %}{{ detail_title }} - LUMRA{% endblock %}

{% block content %}
  {% include 'base/navbar.html' %}
  {% include 'base/sidebar.html' %}

  <div class="main-content px-6 py-6">
    <!-- Breadcrumb -->
    {% include 'base/partials/breadcrumb.html' with breadcrumb_items=breadcrumb %}

    <!-- Header with Actions -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-3xl font-bold text-slate-100">{{ detail_title }}</h1>
      <div class="flex gap-3">
        <a href="{% url edit_view_name pk=object.pk %}" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition">
          <i class="fas fa-pen"></i> Edit
        </a>
        <button onclick="deleteItem()" class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition">
          <i class="fas fa-trash"></i> Hapus
        </button>
      </div>
    </div>

    <!-- Detail Card -->
    <div class="bg-gradient-to-b from-slate-900 to-slate-800 rounded-lg border border-slate-700 overflow-hidden shadow-lg">
      <div class="p-8">
        <!-- Content goes here -->
        <div class="grid grid-cols-2 gap-6">
          <div>
            <p class="text-slate-400 text-sm">Field Name</p>
            <p class="text-slate-100 font-medium">{{ object.field }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Confirmation Modal -->
  {% include 'base/partials/confirm_modal.html' with modal_title="Hapus Item?" modal_message="Yakin ingin menghapus item ini?" %}
{% endblock %}
'''

TEMPLATE_DASHBOARD = '''{% extends 'base/base.html' %}

{% block title %}{{ dashboard_title }} - LUMRA{% endblock %}

{% block content %}
  {% include 'base/navbar.html' %}
  {% include 'base/sidebar.html' %}

  <div class="main-content px-6 py-6">
    <h1 class="text-3xl font-bold text-slate-100 mb-6">{{ dashboard_title }}</h1>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {% include 'base/kpi_card.html' with kpi_title="Total" kpi_value=total %}
      {% include 'base/kpi_card.html' with kpi_title="Active" kpi_value=active %}
      {% include 'base/kpi_card.html' with kpi_title="Pending" kpi_value=pending %}
      {% include 'base/kpi_card.html' with kpi_title="Completed" kpi_value=completed %}
    </div>

    <!-- Main Content -->
    <div class="bg-gradient-to-b from-slate-900 to-slate-800 rounded-lg border border-slate-700 p-8">
      <!-- Content goes here -->
    </div>
  </div>
{% endblock %}
'''

# Define all files to create
FILES_TO_CREATE = {
    # Accounting Module
    'accounting/chart_of_accounts.html': TEMPLATE_LIST,
    'accounting/chart_of_accounts_form.html': TEMPLATE_FORM,
    'accounting/general_ledger.html': TEMPLATE_LIST,
    'accounting/journal_entry_list.html': TEMPLATE_LIST,
    'accounting/journal_entry_form.html': TEMPLATE_FORM,
    'accounting/journal_entry_detail.html': TEMPLATE_DETAIL,
    'accounting/payment_voucher_form.html': TEMPLATE_FORM,
    'accounting/trial_balance.html': TEMPLATE_DASHBOARD,
    'accounting/balance_sheet.html': TEMPLATE_DASHBOARD,
    'accounting/cash_flow.html': TEMPLATE_DASHBOARD,
    'accounting/accounts_receivable.html': TEMPLATE_DASHBOARD,
    'accounting/accounts_payable.html': TEMPLATE_DASHBOARD,

    # Inventory - Additional
    'inventory/batch_list.html': TEMPLATE_LIST,
    'inventory/batch_form.html': TEMPLATE_FORM,
    'inventory/batch_detail.html': TEMPLATE_DETAIL,
    'inventory/requisition_list.html': TEMPLATE_LIST,
    'inventory/requisition_form.html': TEMPLATE_FORM,
    'inventory/requisition_detail.html': TEMPLATE_DETAIL,
    'inventory/adjustment_reasons.html': TEMPLATE_LIST,
    'inventory/expiry_tracking.html': TEMPLATE_LIST,
    'inventory/supplier_evaluation.html': TEMPLATE_DASHBOARD,
    'inventory/warehouse_zones.html': TEMPLATE_LIST,
    'inventory/warehouse_zone_form.html': TEMPLATE_FORM,

    # Marketing
    'marketing/voucher_list.html': TEMPLATE_LIST,
    'marketing/voucher_form.html': TEMPLATE_FORM,
    'marketing/voucher_claim_log.html': TEMPLATE_LIST,
    'marketing/customer_segment_list.html': TEMPLATE_LIST,
    'marketing/customer_segment_form.html': TEMPLATE_FORM,
    'marketing/promotion_calendar.html': TEMPLATE_DASHBOARD,

    # Master Data
    'master_data/bank_accounts.html': TEMPLATE_LIST,
    'master_data/bank_account_form.html': TEMPLATE_FORM,
    'master_data/payment_terms_list.html': TEMPLATE_LIST,
    'master_data/payment_terms_form.html': TEMPLATE_FORM,
    'master_data/tax_list.html': TEMPLATE_LIST,
    'master_data/tax_form.html': TEMPLATE_FORM,
    'master_data/reason_codes.html': TEMPLATE_LIST,
    'master_data/tags_list.html': TEMPLATE_LIST,

    # Messages
    'messages/inbox.html': TEMPLATE_LIST,
    'messages/message_detail.html': TEMPLATE_DETAIL,
    'messages/compose.html': TEMPLATE_FORM,
    'messages/broadcast.html': TEMPLATE_FORM,
    'messages/message_templates.html': TEMPLATE_LIST,

    # Onboarding
    'onboarding/welcome.html': TEMPLATE_DASHBOARD,
    'onboarding/step_business.html': TEMPLATE_FORM,
    'onboarding/step_location.html': TEMPLATE_FORM,
    'onboarding/step_category.html': TEMPLATE_FORM,
    'onboarding/step_complete.html': TEMPLATE_DASHBOARD,

    # Print Templates
    'print/print_invoice.html': TEMPLATE_DASHBOARD,
    'print/print_sales_order.html': TEMPLATE_DASHBOARD,
    'print/print_quotation.html': TEMPLATE_DASHBOARD,
    'print/print_purchase_order.html': TEMPLATE_DASHBOARD,
    'print/print_delivery_note.html': TEMPLATE_DASHBOARD,
    'print/print_packing_slip.html': TEMPLATE_DASHBOARD,
    'print/print_payment_receipt.html': TEMPLATE_DASHBOARD,
    'print/print_receipt.html': TEMPLATE_DASHBOARD,
    'print/print_production_order.html': TEMPLATE_DASHBOARD,
    'print/print_credit_note.html': TEMPLATE_DASHBOARD,
    'print/print_stock_opname.html': TEMPLATE_DASHBOARD,

    # Production
    'production/bom_list.html': TEMPLATE_LIST,
    'production/bom_form.html': TEMPLATE_FORM,
    'production/bom_detail.html': TEMPLATE_DETAIL,
    'production/production_order_list.html': TEMPLATE_LIST,
    'production/production_order_form.html': TEMPLATE_FORM,
    'production/production_order_detail.html': TEMPLATE_DETAIL,
    'production/production_scheduling.html': TEMPLATE_DASHBOARD,
    'production/finished_goods_receipt.html': TEMPLATE_FORM,
    'production/material_consumption.html': TEMPLATE_LIST,
    'production/production_costing.html': TEMPLATE_DASHBOARD,
    'production/production_waste.html': TEMPLATE_LIST,

    # Reports - Additional
    'reports/report_expiry.html': TEMPLATE_DASHBOARD,
    'reports/report_inventory_age.html': TEMPLATE_DASHBOARD,
    'reports/report_customer_lifetime.html': TEMPLATE_DASHBOARD,
    'reports/report_production.html': TEMPLATE_DASHBOARD,
    'reports/report_staff_performance.html': TEMPLATE_DASHBOARD,

    # Sales
    'sales/salesorder_and_quotation/sales_order_list.html': TEMPLATE_LIST,
    'sales/salesorder_and_quotation/sales_order_form.html': TEMPLATE_FORM,
    'sales/salesorder_and_quotation/sales_order_detail.html': TEMPLATE_DETAIL,
    'sales/salesorder_and_quotation/quotation_list.html': TEMPLATE_LIST,
    'sales/salesorder_and_quotation/quotation_form.html': TEMPLATE_FORM,
    'sales/salesorder_and_quotation/quotation_detail.html': TEMPLATE_DETAIL,
    'sales/invoice_and_billing/invoice_list.html': TEMPLATE_LIST,
    'sales/invoice_and_billing/invoice_form.html': TEMPLATE_FORM,
    'sales/invoice_and_billing/invoice_detail.html': TEMPLATE_DETAIL,
    'sales/invoice_and_billing/payment_list.html': TEMPLATE_LIST,
    'sales/invoice_and_billing/payment_form.html': TEMPLATE_FORM,
    'sales/retur_and_refund/retur_list.html': TEMPLATE_LIST,
    'sales/retur_and_refund/retur_form.html': TEMPLATE_FORM,
    'sales/retur_and_refund/retur_detail.html': TEMPLATE_DETAIL,

    # Settings
    'settings/roles.html': TEMPLATE_LIST,
    'settings/role_form.html': TEMPLATE_FORM,
    'settings/permission_matrix.html': TEMPLATE_DASHBOARD,
    'settings/email_settings.html': TEMPLATE_FORM,
    'settings/notification_settings.html': TEMPLATE_FORM,
    'settings/numbering_settings.html': TEMPLATE_FORM,
    'settings/backup_restore.html': TEMPLATE_DASHBOARD,
    'settings/api_keys.html': TEMPLATE_LIST,
}

def create_files():
    """Create all HTML template files"""
    created = 0
    updated = 0
    errors = []

    for filepath, content in FILES_TO_CREATE.items():
        full_path = BASE_PATH / filepath
        
        # Create directory if not exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Check if file exists and if it's empty or needs update
            if full_path.exists():
                existing_size = full_path.stat().st_size
                if existing_size < 200:  # Small/empty file
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated += 1
                    print(f"✓ Updated: {filepath}")
                else:
                    print(f"- Skipped: {filepath} (already has content)")
            else:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                created += 1
                print(f"✓ Created: {filepath}")
        except Exception as e:
            errors.append(f"✗ Error: {filepath} - {str(e)}")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Created: {created} files")
    print(f"  Updated: {updated} files")
    if errors:
        print(f"  Errors: {len(errors)} files")
        for error in errors:
            print(f"    {error}")
    print(f"{'='*60}")

if __name__ == '__main__':
    create_files()
