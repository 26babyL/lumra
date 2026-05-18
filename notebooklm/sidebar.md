{% load static %}

<!--{# ═══════════════════════════════════════════════════════════════════
   SIDEBAR — Lumra ERP · Emerald Odyssey
   "You use other ERPs to run a business.
    You use Lumra when you are building an empire."

   Filosofi : Glass Protocol · Collapse ke icon-only · Accordion rapi
   Stack    : Django + Alpine.js

   TIDAK ADA inline CSS di file ini — semua style dari:
   · lumra_tokens.css     → --sb-* tokens, palette, spacing
   · lumra_components.css → §17 Sidebar Glass (nav-item, sub-item, dll)
   · lumra_sidebar.css    → suplemen (sb-header-border, badge-new,
                             theme-toggle, sb-logout-btn, icon-fix)
   Hirarki  : Operations → Logistics → Analytics → Configuration
═══════════════════════════════════════════════════════════════════ #}-->

<aside
  id="sidebar"
  class="sidebar-glass fixed inset-y-0 left-0 md:static z-40 relative flex flex-col transition-all duration-300 ease-in-out overflow-hidden"
  x-data="{
    open  : (JSON.parse(localStorage.getItem('sidebarOpen') || 'true')) && window.innerWidth >= 768,
    mobile: window.innerWidth < 768,
    menu  : null,

    menuMap: {
      operations: ['/dashboard/', '/inventory/', '/products/', '/pos/', '/stock-planning/'],
      logistics  : ['/purchasing/', '/supplier-price-list/', '/locations/', '/stock-movement/'],
      analytics  : ['/sales/', '/insights/', '/financial-reports/', '/market-insights/', '/trends/', '/reports/'],
      config     : ['/settings/', '/users/', '/business-settings/', '/system-status/', '/master/', '/about/', '/contact/', '/pricing/'],
    },

    init() {
      for (const [key, paths] of Object.entries(this.menuMap)) {
        if (paths.some(p => window.location.pathname.startsWith(p))) {
          this.menu = key; break;
        }
      }
      document.body.classList.toggle('sidebar-open', this.open);
      this.$watch('open', v => {
        localStorage.setItem('sidebarOpen', v);
        document.body.classList.toggle('sidebar-open', v);
      });
      window.addEventListener('resize', () => {
        this.mobile = window.innerWidth < 768;
        if (this.mobile) this.open = false;
        else this.open = JSON.parse(localStorage.getItem('sidebarOpen') || 'true');
      });
      window.addEventListener('toggle-sidebar',       () => { this.open = !this.open; });
      window.addEventListener('lumra:toggle-sidebar', () => { this.open = !this.open; });
    },

    toggle(name) { this.menu = this.menu === name ? null : name; },
    active(path)     { return window.location.pathname.startsWith(path); },
    anyActive(paths) { return paths.some(p => window.location.pathname.startsWith(p)); },
  }"
  @keydown.window.escape="if (mobile) open = false"
  :class="open ? 'w-[220px]' : 'w-[60px] -translate-x-full md:translate-x-0'"
  role="navigation"
  aria-label="Sidebar navigation">

  <!--{# ── Blob dekoratif — depth untuk glass effect ── #}-->
  <div class="sb-blob sb-blob-1" aria-hidden="true"></div>
  <div class="sb-blob sb-blob-2" aria-hidden="true"></div>

  <!--{# ════════════════════════════════════════════════════════
     HEADER — Logo & collapse toggle
  ════════════════════════════════════════════════════════ #}-->
  <div class="flex-shrink-0 flex items-center h-14 px-3 sb-header-border"
       :class="open ? 'justify-between' : 'justify-center'">

    <a href="{% url 'dashboard' %}"
       class="flex items-center gap-2.5 min-w-0"
       aria-label="Lumra ERP Home">
      <div class="logo-icon">
        <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
          <path d="M2 21v-2h2V3h14v2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2v6h2v2H2zm4-2h8V5H6v14zm10-6h2V7h-2v6z"/>
        </svg>
      </div>
      <span
        x-show="open"
        x-transition:enter="transition duration-200"
        x-transition:enter-start="opacity-0 -translate-x-2"
        x-transition:enter-end="opacity-100 translate-x-0"
        x-transition:leave="transition duration-100"
        x-transition:leave-end="opacity-0"
        class="font-bold text-[15px] truncate sb-username">
        Lumra ERP
      </span>
    </a>

    <!--{# Collapse button — expanded mode #}-->
    <button
      x-show="open"
      x-transition.opacity
      @click="open = false"
      class="collapse-btn"
      aria-label="Tutup sidebar">
      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
      </svg>
    </button>
  </div>

  <!--{# Expand button — floating di kanan, desktop collapsed mode #}-->
  <button
    x-show="!open"
    x-cloak
    @click="open = true"
    class="hidden md:flex absolute right-0 top-[60px] translate-x-1/2 collapse-btn shadow-md z-50"
    aria-label="Buka sidebar">
    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
    </svg>
  </button>

  <!--{# ════════════════════════════════════════════════════════
     NAVIGATION
  ════════════════════════════════════════════════════════ #}-->
  <nav class="nav-scroll flex-1 overflow-y-auto overflow-x-hidden py-3 px-2 space-y-0.5"
       role="menu">

    <!--{# ── SECTION 1: OPERATIONS ── #}-->
    <p class="nav-section" :class="!open ? 'opacity-0' : ''">Operations</p>

    <!--{# Dashboard #}-->
    <a href="{% url 'dashboard' %}"
       class="nav-item"
       :class="[active('/dashboard/') ? 'active' : '', !open ? 'collapsed' : '']"
       role="menuitem">
      <div class="nav-icon-wrap">
        <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
          <rect x="3"  y="3"  width="7" height="7" rx="1.5"/>
          <rect x="14" y="3"  width="7" height="7" rx="1.5"/>
          <rect x="3"  y="14" width="7" height="7" rx="1.5"/>
          <rect x="14" y="14" width="7" height="7" rx="1.5"/>
        </svg>
      </div>
      <span x-show="open" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0 -translate-x-1" x-transition:enter-end="opacity-100 translate-x-0" x-transition:leave="transition ease-in duration-100" x-transition:leave-end="opacity-0" class="flex-1 truncate">Dashboard</span>
      <span class="nav-tooltip" x-show="!open">Dashboard</span>
    </a>

    <!--{# Point of Sale #}-->
    <a href="{% url 'pos' %}"
       class="nav-item"
       :class="[active('/pos/') ? 'active' : '', !open ? 'collapsed' : '']"
       role="menuitem">
      <div class="nav-icon-wrap">
        <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
          <rect x="2" y="3" width="20" height="14" rx="2"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M8 21h8m-4-4v4"/>
        </svg>
      </div>
      <span x-show="open" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0 -translate-x-1" x-transition:enter-end="opacity-100 translate-x-0" x-transition:leave="transition ease-in duration-100" x-transition:leave-end="opacity-0" class="flex-1 truncate">Point of Sale</span>
      <span class="nav-tooltip" x-show="!open">Point of Sale</span>
    </a>

    <!--{# Inventory — accordion #}-->
    <div>
      <button
        @click="toggle('operations')"
        :aria-expanded="(menu === 'operations').toString()"
        class="nav-item"
        :class="[anyActive(['/inventory/','/products/','/stock-planning/','/stock-movement/']) ? 'parent-active' : '', !open ? 'collapsed' : '']">
        <div class="nav-icon-wrap">
          <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0v10l-8 4m0-14L4 17m8-10v14"/>
          </svg>
        </div>
        <span x-show="open" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0 -translate-x-1" x-transition:enter-end="opacity-100 translate-x-0" x-transition:leave="transition ease-in duration-100" x-transition:leave-end="opacity-0" class="flex-1 truncate text-left">Inventory</span>
        <svg x-show="open" class="nav-icon chevron" :class="menu==='operations'?'open':''" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
        <span class="nav-tooltip" x-show="!open">Inventory</span>
      </button>
      <div class="submenu-container"
           x-show="menu === 'operations' && open"
           x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0" x-transition:enter-end="opacity-100"
           x-transition:leave="transition ease-in duration-150" x-transition:leave-end="opacity-0"
           x-cloak>
        <div class="pl-7 pt-1 pb-1 space-y-0.5">
          <a href="{% url 'products' %}"       class="sub-item" :class="active('/products/')       ? 'active' : ''">Stock Overview</a>
          <a href="{% url 'stock_planning' %}" class="sub-item" :class="active('/stock-planning/') ? 'active' : ''">Stock Planning</a>
          <a href="{% url 'stock_movement' %}" class="sub-item" :class="active('/stock-movement/') ? 'active' : ''">Stock Movement</a>
        </div>
      </div>
    </div>

    <!--{# ── SECTION 2: LOGISTICS ── #}-->
    <p class="nav-section" :class="!open ? 'opacity-0' : ''">Logistics</p>

    <!--{# Locations #}-->
    <a href="{% url 'locations' %}"
       class="nav-item"
       :class="[active('/locations/') ? 'active' : '', !open ? 'collapsed' : '']"
       role="menuitem">
      <div class="nav-icon-wrap">
        <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
      </div>
      <span x-show="open" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0 -translate-x-1" x-transition:enter-end="opacity-100 translate-x-0" x-transition:leave="transition ease-in duration-100" x-transition:leave-end="opacity-0" class="flex-1 truncate">Locations</span>
      <span class="nav-tooltip" x-show="!open">Locations</span>
    </a>

    <!--{# Procurement — accordion #}-->
    <div>
      <button
        @click="toggle('logistics')"
        :aria-expanded="(menu === 'logistics').toString()"
        class="nav-item"
        :class="[anyActive(['/purchasing/','/supplier-price-list/']) ? 'parent-active' : '', !open ? 'collapsed' : '']">
        <div class="nav-icon-wrap">
          <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/>
          </svg>
        </div>
        <span x-show="open" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0 -translate-x-1" x-transition:enter-end="opacity-100 translate-x-0" x-transition:leave="transition ease-in duration-100" x-transition:leave-end="opacity-0" class="flex-1 truncate text-left">Procurement</span>
        <svg x-show="open" class="nav-icon chevron" :class="menu==='logistics'?'open':''" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
        <span class="nav-tooltip" x-show="!open">Procurement</span>
      </button>
      <div class="submenu-container"
           x-show="menu === 'logistics' && open"
           x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0" x-transition:enter-end="opacity-100"
           x-transition:leave="transition ease-in duration-150" x-transition:leave-end="opacity-0"
           x-cloak>
        <div class="pl-7 pt-1 pb-1 space-y-0.5">
          <a href="{% url 'purchasing' %}"          class="sub-item" :class="active('/purchasing/')          ? 'active' : ''">Purchasing</a>
          <a href="{% url 'supplier_price_list' %}" class="sub-item" :class="active('/supplier-price-list/') ? 'active' : ''">Supplier Prices</a>
          <a href="{% url 'vendors_list' %}"        class="sub-item" :class="active('/master/vendors')       ? 'active' : ''">Vendors</a>
        </div>
      </div>
    </div>

    <!--{# ── SECTION 3: ANALYTICS ── #}-->
    <p class="nav-section" :class="!open ? 'opacity-0' : ''">Analytics</p>

    <!--{# Customers #}-->
    <a href="{% url 'customer_list' %}"
       class="nav-item"
       :class="[active('/master/customers/') ? 'active' : '', !open ? 'collapsed' : '']"
       role="menuitem">
      <div class="nav-icon-wrap">
        <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
      </div>
      <span x-show="open" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0 -translate-x-1" x-transition:enter-end="opacity-100 translate-x-0" x-transition:leave="transition ease-in duration-100" x-transition:leave-end="opacity-0" class="flex-1 truncate">Customers</span>
      <span class="nav-tooltip" x-show="!open">Customers</span>
    </a>

    <!--{# Sales & Insights — accordion #}-->
    <div>
      <button
        @click="toggle('analytics')"
        :aria-expanded="(menu === 'analytics').toString()"
        class="nav-item"
        :class="[anyActive(['/sales/','/insights/','/financial-reports/','/market-insights/','/trends/']) ? 'parent-active' : '', !open ? 'collapsed' : '']">
        <div class="nav-icon-wrap">
          <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
        </div>
        <span x-show="open" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0 -translate-x-1" x-transition:enter-end="opacity-100 translate-x-0" x-transition:leave="transition ease-in duration-100" x-transition:leave-end="opacity-0" class="flex-1 truncate text-left">Sales & Insights</span>
        <svg x-show="open" class="nav-icon chevron" :class="menu==='analytics'?'open':''" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
        <span class="nav-tooltip" x-show="!open">Analytics</span>
      </button>
      <div class="submenu-container"
           x-show="menu === 'analytics' && open"
           x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0" x-transition:enter-end="opacity-100"
           x-transition:leave="transition ease-in duration-150" x-transition:leave-end="opacity-0"
           x-cloak>
        <div class="pl-7 pt-1 pb-1 space-y-0.5">
          <a href="{% url 'sales_history' %}"     class="sub-item" :class="active('/sales/history/')           ? 'active' : ''">Sales History</a>
          <a href="{% url 'sales_performance' %}" class="sub-item" :class="active('/sales/performance/')       ? 'active' : ''">Performance</a>
          <a href="{% url 'financial_reports' %}" class="sub-item" :class="active('/sales/financial-reports/') ? 'active' : ''">Financial Reports</a>
          <a href="{% url 'market_insights' %}"   class="sub-item" :class="active('/market-insights/')         ? 'active' : ''">Market Insights</a>
          <a href="{% url 'trends_analysis' %}"   class="sub-item" :class="active('/trends/')                  ? 'active' : ''">Trends</a>
          <a href="{% url 'activity_log' %}"      class="sub-item" :class="active('/activity-log/')            ? 'active' : ''">Activity Log</a>
        </div>
      </div>
    </div>

    <!--{# Reports — accordion #}-->
    <div>
      <button
        @click="toggle('reports')"
        :aria-expanded="(menu === 'reports').toString()"
        class="nav-item"
        :class="[anyActive(['/reports/']) ? 'parent-active' : '', !open ? 'collapsed' : '']">
        <div class="nav-icon-wrap">
          <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
        </div>
        <span x-show="open" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0 -translate-x-1" x-transition:enter-end="opacity-100 translate-x-0" x-transition:leave="transition ease-in duration-100" x-transition:leave-end="opacity-0" class="flex-1 truncate text-left">Reports</span>
        <svg x-show="open" class="nav-icon chevron" :class="menu==='reports'?'open':''" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
        <span class="nav-tooltip" x-show="!open">Reports</span>
      </button>
      <div class="submenu-container"
           x-show="menu === 'reports' && open"
           x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0" x-transition:enter-end="opacity-100"
           x-transition:leave="transition ease-in duration-150" x-transition:leave-end="opacity-0"
           x-cloak>
        <div class="pl-7 pt-1 pb-1 space-y-0.5">
          <a href="{% url 'sales_report' %}"              class="sub-item" :class="active('/reports/sales/')              ? 'active' : ''">Sales Report</a>
          <a href="{% url 'transaction_summary' %}"       class="sub-item" :class="active('/reports/transactions/')       ? 'active' : ''">Transactions</a>
          <a href="{% url 'transfer_report' %}"           class="sub-item" :class="active('/reports/transfers/')          ? 'active' : ''">Transfers</a>
          <a href="{% url 'requisition_report' %}"        class="sub-item" :class="active('/reports/requisitions/')       ? 'active' : ''">Requisitions</a>
          <a href="{% url 'purchasing_report' %}"         class="sub-item" :class="active('/reports/purchasing/')         ? 'active' : ''">Purchasing</a>
          <a href="{% url 'report_inventory_log' %}"      class="sub-item" :class="active('/reports/inventory-log/')      ? 'active' : ''">Inventory Log</a>
          <a href="{% url 'report_inventory_low' %}"      class="sub-item" :class="active('/reports/inventory-low/')      ? 'active' : ''">Low Stock</a>
          <a href="{% url 'report_inventory_stock' %}"    class="sub-item" :class="active('/reports/inventory-stock/')    ? 'active' : ''">Inventory Stock</a>
          <a href="{% url 'report_profit_loss_detail' %}" class="sub-item" :class="active('/reports/profit-loss-detail/') ? 'active' : ''">P/L Detail</a>
          <a href="{% url 'report_sales_by_outlet' %}"    class="sub-item" :class="active('/reports/sales-by-outlet/')    ? 'active' : ''">Sales by Outlet</a>
          <a href="{% url 'report_sales_by_payment' %}"   class="sub-item" :class="active('/reports/sales-by-payment/')   ? 'active' : ''">Sales by Payment</a>
          <a href="{% url 'report_sales_by_product' %}"   class="sub-item" :class="active('/reports/sales-by-product/')   ? 'active' : ''">Sales by Product</a>
          <a href="{% url 'report_sales_summary' %}"      class="sub-item" :class="active('/reports/sales-summary/')      ? 'active' : ''">Sales Summary</a>
        </div>
      </div>
    </div>

    <!--{# ── SECTION 4: CONFIGURATION ── #}-->
    <p class="nav-section" :class="!open ? 'opacity-0' : ''">Configuration</p>

    <!--{# Notifications #}-->
    <a href="{% url 'notification' %}"
       class="nav-item"
       :class="[active('/notifications/') ? 'active' : '', !open ? 'collapsed' : '']"
       role="menuitem">
      <div class="nav-icon-wrap">
        <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-5-5.917V4a1 1 0 00-2 0v1.083A6 6 0 006 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
        </svg>
      </div>
      <span x-show="open" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0 -translate-x-1" x-transition:enter-end="opacity-100 translate-x-0" x-transition:leave="transition ease-in duration-100" x-transition:leave-end="opacity-0" class="flex-1 truncate">Notifications</span>
      <span x-show="open && {{ notifications_count|default:0 }} > 0"
            class="lumra-badge-new">
        {{ notifications_count|default:'' }}
      </span>
      <span class="nav-tooltip" x-show="!open">Notifications</span>
    </a>

    <!--{# Master Data — accordion #}-->
    <div>
      <button
        @click="toggle('masterdata')"
        :aria-expanded="(menu === 'masterdata').toString()"
        class="nav-item"
        :class="[anyActive(['/master/']) ? 'parent-active' : '', !open ? 'collapsed' : '']">
        <div class="nav-icon-wrap">
          <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
            <ellipse cx="12" cy="5" rx="9" ry="3"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 12c0 1.657-4.03 3-9 3S3 13.657 3 12"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 5v14c0 1.657 4.03 3 9 3s9-1.343 9-3V5"/>
          </svg>
        </div>
        <span x-show="open" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0 -translate-x-1" x-transition:enter-end="opacity-100 translate-x-0" x-transition:leave="transition ease-in duration-100" x-transition:leave-end="opacity-0" class="flex-1 truncate text-left">Master Data</span>
        <svg x-show="open" class="nav-icon chevron" :class="menu==='masterdata'?'open':''" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
        <span class="nav-tooltip" x-show="!open">Master Data</span>
      </button>
      <div class="submenu-container"
           x-show="menu === 'masterdata' && open"
           x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0" x-transition:enter-end="opacity-100"
           x-transition:leave="transition ease-in duration-150" x-transition:leave-end="opacity-0"
           x-cloak>
        <div class="pl-7 pt-1 pb-1 space-y-0.5">
          <a href="{% url 'categories_list' %}"       class="sub-item" :class="active('/master/categories')   ? 'active' : ''">Categories</a>
          <a href="{% url 'units_list' %}"             class="sub-item" :class="active('/master/units')        ? 'active' : ''">Units</a>
          <a href="{% url 'vendors_list' %}"           class="sub-item" :class="active('/master/vendors')      ? 'active' : ''">Vendors</a>
          <a href="{% url 'stock_opname_locations' %}" class="sub-item" :class="active('/master/stock-opname') ? 'active' : ''">Stock Opname</a>
          <a href="{% url 'customer_list' %}"          class="sub-item" :class="active('/master/customers')    ? 'active' : ''">Customers</a>
        </div>
      </div>
    </div>

    <!--{# Settings — accordion #}-->
    <div>
      <button
        @click="toggle('config')"
        :aria-expanded="(menu === 'config').toString()"
        class="nav-item"
        :class="[anyActive(['/settings/','/users/','/business-settings/','/system-status/']) ? 'parent-active' : '', !open ? 'collapsed' : '']">
        <div class="nav-icon-wrap">
          <svg class="nav-icon" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </div>
        <span x-show="open" x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0 -translate-x-1" x-transition:enter-end="opacity-100 translate-x-0" x-transition:leave="transition ease-in duration-100" x-transition:leave-end="opacity-0" class="flex-1 truncate text-left">Settings</span>
        <svg x-show="open" class="nav-icon chevron" :class="menu==='config'?'open':''" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
        <span class="nav-tooltip" x-show="!open">Settings</span>
      </button>
      <div class="submenu-container"
           x-show="menu === 'config' && open"
           x-transition:enter="transition ease-out duration-200" x-transition:enter-start="opacity-0" x-transition:enter-end="opacity-100"
           x-transition:leave="transition ease-in duration-150" x-transition:leave-end="opacity-0"
           x-cloak>
        <div class="pl-7 pt-1 pb-1 space-y-0.5">
          <a href="{% url 'users' %}"             class="sub-item" :class="active('/users/')             ? 'active' : ''">Users & Roles</a>
          <a href="{% url 'business_settings' %}" class="sub-item" :class="active('/business-settings/') ? 'active' : ''">Business</a>
          <a href="{% url 'system_status' %}"     class="sub-item" :class="active('/system-status/')     ? 'active' : ''">System Status</a>
          <a href="{% url 'about' %}"             class="sub-item" :class="active('/about/')             ? 'active' : ''">About</a>
        </div>
      </div>
    </div>

  </nav>

  <!--{# ════════════════════════════════════════════════════════
     FOOTER — Theme toggle + User profile
  ════════════════════════════════════════════════════════ #}-->
  <div class="flex-shrink-0 sb-footer-border px-2 py-3">

    <!--{# Theme toggle — expanded #}-->
    <div class="mb-2" x-show="open" x-transition.opacity>
      <button
        class="lumra-theme-toggle"
        onclick="lumraToggleTheme()"
        aria-label="Toggle dark/light mode">
        <div class="lumra-theme-toggle-track"></div>
        <span class="lumra-theme-toggle-label"></span>
      </button>
    </div>

    <!--{# Theme toggle — collapsed (icon only) #}-->
    <div class="flex justify-center mb-2" x-show="!open" x-cloak>
      <button
        onclick="lumraToggleTheme()"
        class="collapse-btn"
        aria-label="Toggle dark/light mode"
        title="Toggle theme">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="4"/>
          <path stroke-linecap="round" d="M12 2v2M12 20v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M2 12h2M20 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
        </svg>
      </button>
    </div>

    <!--{# User profile row #}-->
    <div class="flex items-center gap-2.5"
         :class="open ? '' : 'justify-center'">

      <!--{# Avatar #}-->
      <div class="relative flex-shrink-0 cursor-pointer"
           @click="window.location.href = '{% url 'profile' %}'">
        <img
          src="{{ user.profile.avatar.url|default:'/static/img/default-avatar.png' }}"
          class="w-8 h-8 rounded-full object-cover transition-all"
          alt="{{ user.get_full_name|default:user.username }}">
        <span class="online-dot"></span>
        <span class="nav-tooltip" x-show="!open">{{ user.get_full_name|default:user.username }}</span>
      </div>

      <!--{# Info + logout — expanded only #}-->
      <div
        x-show="open"
        x-transition:enter="transition duration-200" x-transition:enter-start="opacity-0" x-transition:enter-end="opacity-100"
        x-transition:leave="transition duration-100" x-transition:leave-end="opacity-0"
        class="flex-1 min-w-0 flex items-center justify-between gap-1">

        <div class="min-w-0">
          <a href="{% url 'profile' %}"
             class="block text-[13px] font-semibold sb-username truncate leading-tight transition-colors hover:text-emerald-600">
            {{ user.get_full_name|default:user.username }}
          </a>
          <p class="text-[11px] sb-role truncate leading-tight mt-0.5">
            {{ user.profile.role|default:"Admin" }}
          </p>
        </div>

        <a href="{% url 'logout' %}"
           class="sb-logout-btn"
           title="Keluar"
           aria-label="Keluar">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
        </a>
      </div>
    </div>
  </div>

</aside>