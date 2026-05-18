"""
COPY-PASTE READY TEMPLATES FOR ACCOUNTING MODULE MIGRATION
Templates ready to use for the remaining 10 templates
"""

# ============================================================================
# PATTERN 1: Simple List + Filter (Use for: chart_of_accounts_form)
# ============================================================================

SIMPLE_LIST_PATTERN = '''
{# Example: chart_of_accounts_form.html - but extracted to list view #}

{% extends 'base/base.html' %}
{% block title %}Daftar Akun — CoffeeShop{% endblock %}

{% block content %}
<div class="w-full flex-1 space-y-6" x-data="accountListApp()" x-init="init()" x-cloak>
  
  <!-- Header -->
  <div class="flex items-end justify-between">
    <div>
      <h1 class="text-2xl font-bold">Daftar Akun</h1>
      <p class="text-sm text-slate-400">{{ total_accounts }} akun terdaftar</p>
    </div>
    <a href="{% url 'chart_of_accounts_form' %}" class="btn-primary">
      <i class="fas fa-plus"></i> Buat Akun Baru
    </a>
  </div>

  <!-- Table -->
  <div class="glass-card">
    <table class="w-full">
      <thead>
        <tr>
          <th class="text-left p-4">Kode Akun</th>
          <th class="text-left p-4">Nama</th>
          <th class="text-left p-4">Tipe</th>
          <th class="text-center p-4">Aksi</th>
        </tr>
      </thead>
      <tbody>
        <template x-for="acc in accounts" :key="acc.id">
          <tr class="border-t">
            <td class="p-4" x-text="acc.code"></td>
            <td class="p-4" x-text="acc.name"></td>
            <td class="p-4" x-text="acc.type"></td>
            <td class="p-4 text-center">
              <a :href="`/accounting/coa/${acc.id}/edit/`" class="text-blue-600">Edit</a>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>

</div>
{% endblock %}

{% block extra_scripts %}
<!-- JSON injection -->
<script id="accounts-list-data" type="application/json">
{{ accounts_json|safe }}
</script>

<script>
function accountListApp() {
  return {
    accounts: [],
    
    init() {
      const raw = document.getElementById('accounts-list-data');
      if (raw) {
        try {
          this.accounts = JSON.parse(raw.textContent);
        } catch(e) {
          console.error('Failed to parse accounts:', e);
          this.accounts = [];
        }
      }
    }
  }
}
</script>
{% endblock %}
'''

# ============================================================================
# PATTERN 2: Complex Report (Use for: balance_sheet, profit_loss_statement)
# ============================================================================

COMPLEX_REPORT_PATTERN = '''
{# Example: balance_sheet.html #}

{% extends 'base/base.html' %}
{% block title %}Neraca (Balance Sheet) — CoffeeShop{% endblock %}

{% block content %}
<div class="w-full flex-1 space-y-6" x-data="balanceSheetApp()" x-init="init()" x-cloak>
  
  <!-- Header -->
  <div>
    <h1 class="text-2xl font-bold">Neraca per {{ as_of_date }}</h1>
    <p class="text-sm text-slate-400">Laporan posisi keuangan</p>
  </div>

  <!-- Assets -->
  <div class="glass-card p-6">
    <h2 class="text-lg font-bold mb-4">ASET</h2>
    
    <!-- Current Assets -->
    <div class="mb-6">
      <p class="font-bold text-slate-700 mb-2">Aset Lancar</p>
      <template x-for="item in currentAssets" :key="item.id">
        <div class="flex justify-between p-2 border-b">
          <span x-text="item.name"></span>
          <span class="font-mono" x-text="formatCurrency(item.balance)"></span>
        </div>
      </template>
      <div class="flex justify-between p-2 font-bold bg-slate-50">
        <span>Total Aset Lancar</span>
        <span x-text="formatCurrency(totalCurrentAssets)"></span>
      </div>
    </div>

    <!-- Fixed Assets -->
    <div class="mb-6">
      <p class="font-bold text-slate-700 mb-2">Aset Tetap</p>
      <template x-for="item in fixedAssets" :key="item.id">
        <div class="flex justify-between p-2 border-b">
          <span x-text="item.name"></span>
          <span class="font-mono" x-text="formatCurrency(item.balance)"></span>
        </div>
      </template>
      <div class="flex justify-between p-2 font-bold bg-slate-50">
        <span>Total Aset Tetap</span>
        <span x-text="formatCurrency(totalFixedAssets)"></span>
      </div>
    </div>

    <!-- Total Assets -->
    <div class="flex justify-between p-2 font-bold text-lg bg-slate-800 text-white">
      <span>TOTAL ASET</span>
      <span x-text="formatCurrency(totalAssets)"></span>
    </div>
  </div>

  <!-- Liabilities & Equity (similar structure) -->
  
</div>
{% endblock %}

{% block extra_scripts %}
<!-- JSON data sections -->
<script id="current-assets-data" type="application/json">
{{ current_assets_json|safe }}
</script>

<script id="fixed-assets-data" type="application/json">
{{ fixed_assets_json|safe }}
</script>

<script id="liabilities-data" type="application/json">
{{ liabilities_json|safe }}
</script>

<script id="equity-data" type="application/json">
{{ equity_json|safe }}
</script>

<script>
function balanceSheetApp() {
  return {
    currentAssets: [],
    fixedAssets: [],
    liabilities: [],
    equity: [],
    
    get totalCurrentAssets() {
      return this.currentAssets.reduce((sum, item) => sum + (item.balance || 0), 0);
    },
    
    get totalFixedAssets() {
      return this.fixedAssets.reduce((sum, item) => sum + (item.balance || 0), 0);
    },
    
    get totalAssets() {
      return this.totalCurrentAssets + this.totalFixedAssets;
    },

    formatCurrency(num) {
      return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
      }).format(num || 0);
    },

    init() {
      // Load current assets
      const caRaw = document.getElementById('current-assets-data');
      if (caRaw) {
        try {
          this.currentAssets = JSON.parse(caRaw.textContent);
        } catch(e) {
          console.error('Failed to parse current assets:', e);
        }
      }
      
      // Load fixed assets
      const faRaw = document.getElementById('fixed-assets-data');
      if (faRaw) {
        try {
          this.fixedAssets = JSON.parse(faRaw.textContent);
        } catch(e) {
          console.error('Failed to parse fixed assets:', e);
        }
      }
      
      // Similar for liabilities, equity
    }
  }
}
</script>
{% endblock %}
'''

# ============================================================================
# PATTERN 3: Form with Data Lists (Use for: journal_entry_form, payment_voucher_form)
# ============================================================================

FORM_WITH_DATA_PATTERN = '''
{# Example: journal_entry_form.html #}

{% extends 'base/base.html' %}
{% block title %}Buat Jurnal — CoffeeShop{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto" x-data="journalFormApp()" x-init="init()" x-cloak>
  
  <form method="post" @submit="handleSubmit" class="space-y-6">
    {% csrf_token %}
    
    <!-- Form fields -->
    <div class="glass-card p-6">
      <label class="block mb-2 font-bold">Pilih Akun</label>
      <select name="account_id" x-model="form.accountId" class="w-full p-3 border rounded">
        <option value="">-- Pilih Akun --</option>
        <template x-for="acc in postingAccounts" :key="acc.id">
          <option :value="acc.id" x-text="acc.code + ' - ' + acc.name"></option>
        </template>
      </select>
    </div>

    <!-- Dynamically added line items -->
    <div class="glass-card p-6">
      <h3 class="font-bold mb-4">Detail Jurnal</h3>
      <template x-for="(line, idx) in lineItems" :key="idx">
        <div class="mb-4 p-4 border rounded">
          <input type="text" x-model="line.description" placeholder="Keterangan" class="w-full p-2 border rounded">
          <input type="number" x-model="line.amount" placeholder="Jumlah" class="w-full p-2 border rounded mt-2">
        </div>
      </template>
      <button type="button" @click="addLineItem()" class="btn-secondary">+ Tambah Baris</button>
    </div>

    <button type="submit" class="btn-primary">Simpan Jurnal</button>
  </form>
</div>
{% endblock %}

{% block extra_scripts %}
<!-- Posting accounts data -->
<script id="posting-accounts-data" type="application/json">
{{ posting_accounts_json|safe }}
</script>

<script>
function journalFormApp() {
  return {
    postingAccounts: [],
    lineItems: [{ description: '', amount: 0 }],
    form: {
      accountId: '',
    },

    addLineItem() {
      this.lineItems.push({ description: '', amount: 0 });
    },

    handleSubmit(event) {
      // Custom submit logic if needed
      // Otherwise form submits normally
    },

    init() {
      const raw = document.getElementById('posting-accounts-data');
      if (raw) {
        try {
          this.postingAccounts = JSON.parse(raw.textContent);
        } catch(e) {
          console.error('Failed to parse accounts:', e);
        }
      }
    }
  }
}
</script>
{% endblock %}
'''

# ============================================================================
# PATTERN 4: Aging/Analysis Table (Use for: stock_movement, aging reports)
# ============================================================================

AGING_TABLE_PATTERN = '''
{# Example: stock_movement.html or aging analysis #}

{% extends 'base/base.html' %}
{% block title %}Gerakan Stok — CoffeeShop{% endblock %}

{% block content %}
<div class="w-full flex-1" x-data="movementApp()" x-init="init()" x-cloak>
  
  <!-- Filters -->
  <div class="glass-card p-4 mb-6 flex gap-4">
    <input type="text" x-model="filters.product" placeholder="Produk..." class="px-3 py-2 border rounded">
    <select x-model="filters.type" @change="filterData()" class="px-3 py-2 border rounded">
      <option value="">Semua Tipe</option>
      <option value="in">Masuk</option>
      <option value="out">Keluar</option>
      <option value="adjustment">Adjustment</option>
    </select>
    <button @click="resetFilters()" class="btn-ghost">Reset</button>
  </div>

  <!-- Data Table -->
  <div class="glass-card overflow-hidden">
    <table class="w-full">
      <thead class="bg-slate-50">
        <tr>
          <th class="text-left p-4">Tanggal</th>
          <th class="text-left p-4">Produk</th>
          <th class="text-left p-4">Tipe</th>
          <th class="text-right p-4">Qty</th>
          <th class="text-right p-4">Saldo</th>
        </tr>
      </thead>
      <tbody>
        <template x-for="item in filteredMovements" :key="item.id">
          <tr class="border-t hover:bg-slate-50">
            <td class="p-4" x-text="item.date"></td>
            <td class="p-4" x-text="item.product_name"></td>
            <td class="p-4">
              <span class="px-2 py-1 rounded text-xs font-bold"
                    :class="getTypeClass(item.type)"
                    x-text="item.type">
              </span>
            </td>
            <td class="p-4 text-right font-mono" x-text="item.quantity"></td>
            <td class="p-4 text-right font-bold" x-text="item.balance"></td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<!-- Movement history data -->
<script id="movements-data" type="application/json">
{{ movements_json|safe }}
</script>

<script>
function movementApp() {
  return {
    allMovements: [],
    filteredMovements: [],
    filters: {
      product: '',
      type: '',
    },

    filterData() {
      this.filteredMovements = this.allMovements.filter(m => {
        const productMatch = !this.filters.product || m.product_name.toLowerCase().includes(this.filters.product.toLowerCase());
        const typeMatch = !this.filters.type || m.type === this.filters.type;
        return productMatch && typeMatch;
      });
    },

    resetFilters() {
      this.filters = { product: '', type: '' };
      this.filterData();
    },

    getTypeClass(type) {
      const classes = {
        'in': 'bg-emerald-100 text-emerald-700',
        'out': 'bg-rose-100 text-rose-700',
        'adjustment': 'bg-amber-100 text-amber-700',
      };
      return classes[type] || 'bg-slate-100 text-slate-700';
    },

    init() {
      const raw = document.getElementById('movements-data');
      if (raw) {
        try {
          this.allMovements = JSON.parse(raw.textContent);
          this.filterData();
        } catch(e) {
          console.error('Failed to parse movements:', e);
        }
      }
    }
  }
}
</script>
{% endblock %}
'''

# ============================================================================
# Print out all patterns
# ============================================================================

if __name__ == '__main__':
    print("=" * 100)
    print("COPY-PASTE READY PATTERNS FOR ACCOUNTING MIGRATION")
    print("=" * 100)
    
    print("\n📋 PATTERN 1: Simple List")
    print("-" * 100)
    print(SIMPLE_LIST_PATTERN)
    
    print("\n\n📊 PATTERN 2: Complex Report")
    print("-" * 100)
    print(COMPLEX_REPORT_PATTERN)
    
    print("\n\n📝 PATTERN 3: Form with Data Lists")
    print("-" * 100)
    print(FORM_WITH_DATA_PATTERN)
    
    print("\n\n📈 PATTERN 4: Aging/Analysis Table")
    print("-" * 100)
    print(AGING_TABLE_PATTERN)
    
    print("\n" + "=" * 100)
    print("HOW TO USE THESE PATTERNS:")
    print("=" * 100)
    print("""
1. Identify which pattern matches your template:
   - Simple lists → Pattern 1
   - Reports → Pattern 2
   - Forms with select/dropdown → Pattern 3
   - Tables with filters → Pattern 4

2. Copy the pattern code

3. Adapt to your specific:
   - Context variable names (accounts_json → your_data_json)
   - Alpine function name (accountListApp → yourFunctionName)
   - Script tag ID (accounts-list-data → unique-id)
   - Table columns and layout
   - Filter fields

4. Test:
   - python manage.py runserver
   - Visit the endpoint
   - View page source to verify script tags
   - Check browser console for errors

5. Repeat for remaining 10 templates
""")
